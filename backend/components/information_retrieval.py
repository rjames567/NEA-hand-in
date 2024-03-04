# -----------------------------------------------------------------------------
# Standard Python library imports
# -----------------------------------------------------------------------------
import itertools
import math

# -----------------------------------------------------------------------------
# Project imports
# -----------------------------------------------------------------------------
import components.books

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def clean_data(string):
    return "".join([i.lower() for i in string if i.isalnum() or i == " "])


# -----------------------------------------------------------------------------
# Objects
# -----------------------------------------------------------------------------
class DocumentCollection:
    def __init__(self, connection, books, authors, genres, result_limit):
        self._authors = authors
        self._genres = genres
        self._books = books
        self._result_limit = result_limit
        self._connection = connection
        self.load_documents_dict()
        self.gen_tf_values()
        self._idf_values = None

    def load_documents_dict(self):
        self._documents_dict = []
        self._documents = []
        res = self._connection.query("""
            SELECT books.clean_title,
                books.book_id,
                authors.clean_name
            FROM books
            INNER JOIN authors ON authors.author_id=books.author_id
        """)
        for title, book_id, author_name in res:
            new_title = title + " " + author_name
            self._documents_dict.append({
                "type": "b",
                "words": new_title,
                "id": book_id,
                "similarity": 0
            })

            self._documents.append(new_title)
        
        for title, genre_id in self._connection.query("SELECT clean_name, genre_id FROM genres"):
            self._documents_dict.append({
                "type": "g",
                "words": title,
                "id": genre_id,
                "similarity": 0
            })
            self._documents.append(title)

        for title, author_id in self._connection.query("SELECT clean_name, author_id FROM authors"):
            self._documents_dict.append({
                "type": "a",
                "words": title,
                "id": author_id,
                "similarity": 0
            })
            self._documents.append(title)

    def gen_unique_words(self):
        words = list(itertools.chain(*[i["words"].split(" ") for i in self._documents_dict]))

        unique_words = set(words)

        self._connection.query("DELETE FROM unique_words")
        values = ""

        for i in unique_words:
            if i != "":
                if values != "":
                    values += ","
                values += f'("{i}")'
        
        self._connection.query(f"INSERT INTO unique_words (word) VALUES {values}")
    
    def gen_tf_values(self, term=None):
        if term is None:
            for count, document in enumerate(self._documents_dict):
                tf = dict()
                arr = document["words"].split(" ")
                one_over_n = 1 / len(arr)
                for i in arr:
                    if i != "":
                        if i in tf:
                            tf[i] += one_over_n
                        else:
                            tf[i] = one_over_n
                self._documents_dict[count]["tf"] = tf
        else:
            arr = term.split(" ")
            tf = dict()
            one_over_n = 1 / len(arr)
            for word in arr:
                if word != "":
                    if word in tf:
                        tf[word] += one_over_n
                    else:
                        tf[word] = one_over_n
            return tf
    
    def num_documents_containing(self, string):
        return sum(string in i for i in self._documents)

    def gen_idf_values(self):
        num_documents = len(self._documents)
        self._idf_values = dict()
        for word_id, word in self._connection.query("SELECT word_id, word FROM unique_words"):
            idf = math.log10(num_documents / self.num_documents_containing(word))
            self._connection.query("""
                UPDATE unique_words
                    SET idf_values={idf}
                WHERE word_id={word_id}
            """.format(
                idf=idf,
                word_id=word_id
            ))

            self._idf_values[word] = idf
    
    @property
    def idf_values(self):
        if self._idf_values is not None: # Should be faster as it only needs to be fetched from the DB once
            return self._idf_values
        else:
            self._idf_values = dict()
            for word, idf in self._connection.query("""SELECT word, idf_values FROM unique_words"""):
                self._idf_values[word] = idf
            return self._idf_values
    
    def gen_tfidf_values(self, document=None, search_terms=None):
        if document is None:
            for count, document in enumerate(self._documents_dict):
                document_words = document["words"].split(" ")
                if search_terms is None:
                    new_search_terms = document_words
                else:
                    new_search_terms = search_terms
                
                res = {i: 0 for i in new_search_terms}
                for i in res.keys():
                    if i in self.idf_values and i in document_words:
                        res[i] = document["tf"][i] * self.idf_values[i]
                
                self._documents_dict[count]["tfidf"] = res
        else:
            document_words = document.split(" ")
            tf = self.gen_tf_values(document)
            res = {i: 0 for i in document_words}
            for i in res.keys():
                if i in self.idf_values and i in document_words:
                    res[i] = tf[i] * self.idf_values[i]
            return res
    
    def tfidf_search(self, terms):
        terms = clean_data(terms)
        term_arr = terms.split(" ")

        search_tfidf = self.gen_tfidf_values(document=terms)
        result = []

        self.gen_tfidf_values(search_terms=term_arr)

        for document in self._documents_dict:
            similarity = a_total = b_total = 0 # These are used to work out the magnitude of the vectors
            tfidf = document["tfidf"]

            for k in term_arr:
                similarity += search_tfidf[k] * tfidf[k]
                a_total += search_tfidf[k] ** 2
                b_total += tfidf[k] ** 2
            
            if similarity > 0:
                similarity /= (math.sqrt(a_total) * math.sqrt(b_total))
                document["similarity"] = similarity
                result.append({
                    "type": document["type"],
                    "similarity": document["similarity"],
                    "id": document["id"]
                })
        
        return sorted(result, key=lambda x: (-x["similarity"], x["type"]))  # Sort by similarity descending and type ascending.
        # This puts authors above books if the rating is the same. Order would be authors -> books -> genres, if the certainty
        # for all of them is the same
    
    def database_search(self, search):
        output_dict = dict()
        addition = 0  # If an isbn result is added, the initial value will be one larger, so would need to be increased by 1
        if search.isnumeric():
            try:
                output_dict[0] = self._books.get_summary(isbn=search)
                output_dict[0]["type"] = "b"
                output_dict[0]["certainty"] = 100.0  # Set certainty to 100% (1 d.p) as it is an exact match
                addition = 1
            except components.books.BookNotFoundError:
                pass
    
        search_result = self.tfidf_search(search)
        for count, res in enumerate(search_result[:self._result_limit - addition]):
            if res["type"] == "b":
                temp = self._books.get_summary(res["id"])
                temp["type"] = "b"
                output_dict[count + addition] = temp
            elif res["type"] == "a":
                temp = {
                    "name": self._authors.id_to_name(res["id"]),
                    "type": "a",
                    "author_id": res["id"]
                }
                output_dict[count + addition] = temp
            else:
                temp = {"name": self._genres.id_to_name(res["id"]), "type": "g"}
                output_dict[count + addition] = temp
            output_dict[count + addition]["certainty"] = round(res["similarity"] * 100, 1)  # Convert similarity to percentage
            # (1 d.p)
        
        return output_dict
