// -----------------------------------------------------------------------------
// Global Variables/Constants
// -----------------------------------------------------------------------------
let disablePopupCancel = false;
let sessionID = null; // Easier to use, allows for if (sessionID)
let currentPage;

// -----------------------------------------------------------------------------
// String Manipulation
// -----------------------------------------------------------------------------
// https://stackoverflow.com/a/6475125/21124864
String.prototype.toTitleCase = function () {
    let str = this.replace(/([^\W_]+[^\s-]*) */g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
    return str;
}

// -----------------------------------------------------------------------------
// URL Manipulation
// -----------------------------------------------------------------------------
function changePageURI (linkName) {
    let newURI;
    if (linkName == "Home") {
        newURI = "/";
    } else {
        newURI = "/" + linkName.toLowerCase().replace(" ", "-");
    }
    history.pushState({urlPath: newURI},"", newURI);
}

function getLinkNameByURI () { // Convert URI to navigation link text.
    let uri = window.location.pathname.replace("-", " ");
    // Replace underscores with spaces
    return uri.slice(1).toTitleCase();
    // Remove leading slash, and convert to title case.
}

// JavaScript for Web Developers    ISBN: 978-1-119-36644-7
function addGetParameter (url, name, value) {
    url += (url.indexOf("?") == -1 ? "?" : "&");
    url += `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;
    return url;
}

// -----------------------------------------------------------------------------
// Page Switching
// -----------------------------------------------------------------------------
function switchPageContent (elem, linkName, async=true) {
    // Does not switch elem to link as using links is very slow, as it needs to
    // iterate through all available link names, to find the correct one.
    if (elem) {
        linkName = $(elem).html();
    }
    if (linkName == "") {
        linkName = "Home" // If it is blank, it must be referring to the Home
        // page.
    }
    let file = "/html/" + linkName.toLowerCase().replace(" ", "_") + ".html";
    changePageContent(file, async, elem, linkName);
    changePageURI(linkName);
}

function reloadCurrentPage () {
    let target_arr = getLinkNameByURI().split("/");
    let target = target_arr[0];
    if (target == "Genre") { // Target is in title case
        switchGenrePage(target_arr[1]);
    } else if (target == "Author") {
        switchAuthorPage(target_arr[1]);
    } else if (target == "Book") {
        switchBookPage(target_arr[1]); //  Needs to be decoded; as on the refresh, any spaces have character
        // codes in, so would be replaced. This avoids double encoding the URL.
    } else { // Manually check the others as they url switching is unnecessary
        switchPageContent(null, getLinkNameByURI());
    }
}

function changePageContent (file, async, elem=null, linkName=null) {
    // Elem and linkName must BOTH be specified, or BOTH must not be specified.
    // Async specifies whether the request is synchronous (false) or asynchronous (true)
    currentPage = linkName;
    $.ajax({
        type: "GET",
        url: file,
        success: function (result) {
            $("main").html(result);
        },
        error: function (jqXHR) {
            $("main").html(jqXHR.responseText);
        },
        complete: function () { // Runs after error/success
            if (elem) { // Allow for both element or link name to be used.
                changeActiveLink(elem, null);
                linkName = $(elem).html();
            } else {
                changeActiveLink(null, linkName);
            }// Navigation links are always updated
            // regardless of success. Improves appeared responsiveness.
            currentPageFunction(linkName);
            $(window).scrollTop(0); // Move user to the top of the window
            assignGenreNavigationHandlers(); // Needs to be in this function as it needs to reassign it based upon the page
            // content.
            assignAuthorNavigationHandlers();
            assignBookNavigationHandlers(); // Needs to be in this function as it needs to reassign it based upon the page
            // content.
            if (linkName != "search") {
                $("header nav.bottom .search form input[type='search']").val(""); // Clear the search bar on page change
            }
        },
        async: async
    });
}

function changeActiveLink (elem, linkContent) {
    $("nav.bottom ul li a.active").removeClass("active");
    if (elem) {
        $(elem).addClass("active");
    } else {
        $("nav.bottom ul li a").each(function () {
            if ($(this).html() == linkContent) {
                $(this).addClass("active");
            }
        });
    }
}

function currentPageFunction (link) {
    checkSignInNecessary(link);
    switch (link) {
        case "My Books":
            loadMyBooks();
            break;
        case "Diary":
            loadDiary();
            break;
        case "Home":
            loadHomePage();
            break;
        case "Recommendations":
            loadRecommendationsPage();
            break;
        case "Browse":
            loadBrowsePage();
            break;
    }
}

$("nav.bottom ul li a").click(function () {
    switchPageContent(this, null);
});

// -----------------------------------------------------------------------------
// Sign In/Sign Up
// -----------------------------------------------------------------------------
function checkSignInNecessary (link) {
    if (["My Books", "Recommendations", "Diary"].includes(link) && !sessionID) {
        $(".account-popups .page-sign-notice").show();
        showSignInPopup();
        return true;
    }
    return false;
}

function hideAllSignPopups () { // Needed so cancel buttons and click-off can be
    // generalised for both.
    if (!disablePopupCancel) {
        if ((["My Books", "Recommendations", "Diary"].includes(currentPage) && !sessionID)) {
            switchPageContent(null, "");  // Redirect to home page if cancelled, and sign in is required.
        }
        $(".account-popups .window").hide();
        hideSignUpAlert(); // Hide popup first then alert to improve perceived responsiveness
        $(".account-popups .page-sign-notice").hide();
    }
}

$(".account-popups button.cancel-button").click(function () {
    hideAllSignPopups();
});

function changeAccountButtons () {
    if (sessionID) {
        $("header nav.top ul li.account-enter").addClass("hidden");
        $("header nav.top ul li.account-exit").removeClass("hidden");
    } else {
        $("header nav.top ul li.account-enter").removeClass("hidden");
        $("header nav.top ul li.account-exit").addClass("hidden");
    }
}

$(window).click(function (event) {
    if ([$("#sign-up")[0],  $("#sign-in")[0]].includes(event.target)
        && !disablePopupCancel) {
        hideAllSignPopups();
    }
});

// -----------------------------------------------------------------------------
// Sign In/Sign Up - Alerts
// -----------------------------------------------------------------------------
function signUpAlert (message) {
    var elem = $(".account-popups p.alert");
    elem.html(message);
    elem.show(); // This order so there is not a delay - minimal so not vital
    timeout = setTimeout(function () {
        elem.fadeOut(500); // Fade out in 1/2 seconds
    }, 8000); // Hide alert after 8 seconds
}

function hideSignUpAlert () {
    $(".account-popups p.alert").hide();
}

// -----------------------------------------------------------------------------
// Sign Up - Popup Visibility
// -----------------------------------------------------------------------------
function showSignUpPopup () {
    $(".account-popups .window#sign-in").hide(); // Hide previous popup
    $(".account-popups .window#sign-up").show();
}

// -----------------------------------------------------------------------------
// Sign Up - Form submission
// -----------------------------------------------------------------------------
$(".account-popups .window#sign-up form").on("submit", function (event) {
    event.preventDefault();
    disablePopupCancel = true;
    let password1 = $(".account-popups #sign-up input[name=password]").val();
    let password2 = $(".account-popups #sign-up input[name=password-repeat]").val();

    let remember = Boolean($(".account-popups #sign-up input[name=remember]:checked").val());

    if (password1 != password2) {
        signUpAlert("Passwords do not match");
        disablePopupCancel = false;
    } else {
        $.ajax({
            type: "POST",
            url: "/cgi-bin/account/sign_up",
            data: JSON.stringify({
                first_name: $(".account-popups #sign-up input[name=first-name]").val(),
                surname: $(".account-popups #sign-up input[name=surname]").val(),
                username: $(".account-popups #sign-up input[name=username]").val(),
                password: password1
            }),
            success: function (result) {
                disablePopupCancel = false; // Cannot go in complete, as it runs
                // after success, so hiding the popup does not work.
                if (result["session_id"]) {
                    sessionID = result["session_id"];
                    changeAccountButtons(); // Change before it can be seen to
                    // appear smoother
                    hideAllSignPopups();
                    reloadCurrentPage();

                    if (remember) {
                        $.cookie.set("sessionID", sessionID, { expires: 50 });
                    }
                } else {
                    signUpAlert(result["message"]);
                }
            },
            error: function () {
                // Error should only run for server-side errors
                signUpAlert("Something went wrong");
                disablePopupCancel = false;
            }
        });
    }
});

// -----------------------------------------------------------------------------
// Sign Up - Link Onclick handlers
// -----------------------------------------------------------------------------
$("a#sign-up-button").click(function () {
    showSignUpPopup();
});

// -----------------------------------------------------------------------------
// Sign In - Popup Visibility
// -----------------------------------------------------------------------------
function showSignInPopup () {
    $(".account-popups .window#sign-in").show(); // For whatever reason, only
    // hide on the showSignUpPopup is needed
}

// -----------------------------------------------------------------------------
// Sign In - Form submission
// -----------------------------------------------------------------------------
$(".account-popups .window#sign-in form").on("submit", function (event) {
    event.preventDefault();
    disablePopupCancel = true;

    let remember = Boolean($(".account-popups #sign-in input[name=remember]:checked").val());

    $.ajax({
        type: "POST",
        url: "/cgi-bin/account/sign_in",
        data: JSON.stringify({
            username: $(".account-popups #sign-in input[name=username]").val(),
            password: $(".account-popups #sign-in input[name=password]").val()
        }),
        success: function (result) {
            disablePopupCancel = false; // Cannot go in complete, as it runs
            // after success, so hiding the popup does not work.
            if (result["session_id"]) {
                sessionID = result["session_id"];
                changeAccountButtons(); // Change before it can be seen to
                // appear smoother
                hideAllSignPopups();
                reloadCurrentPage();
                if (remember) {
                    $.cookie.set("sessionID", sessionID, { expires: 50 });
                }
            } else {
                signUpAlert(result["message"]);
            }
        },
        error: function () {
            // Error should only run for server-side errors
            signUpAlert("Something went wrong");
            disablePopupCancel = false;
        }
    });
});

// -----------------------------------------------------------------------------
// Sign In - Link Onclick handlers
// -----------------------------------------------------------------------------
$("a#sign-in-button").click(function () {
    showSignInPopup();
});

// -----------------------------------------------------------------------------
// Sign Out - Link Onclick handlers
// -----------------------------------------------------------------------------
$("header a#sign-out-button").click(function () {
    $.ajax({
        type: "POST",
        url: "/cgi-bin/account/sign_out",
        data: sessionID
    });
    sessionID = null; // Must come after, as sessionID is needed unaltered
    // Minimal impact on speed, as AJAX is asynchronous
    changeAccountButtons(); // Success does not matter - just improves database
    // maintainability, any non-cleared sessions will be deleted through a
    // maintenance script
    reloadCurrentPage(); // This will be slower, so is done last. This removes any user-specific page content.
    $.cookie.remove("sessionID");
});

// -----------------------------------------------------------------------------
// Session Expiry
// -----------------------------------------------------------------------------
function sessionExpired () {
    sessionID = null;
    if (checkSignInNecessary(currentPage)) {
        showSignInPopup();
    }
    changeAccountButtons();
    $.cookie.remove("sessionID");
}

// -----------------------------------------------------------------------------
// Reading lists
// -----------------------------------------------------------------------------
function loadMyBooks () {
    // Get list titles
    $.ajax({
        type: "GET",
        url: addGetParameter("/cgi-bin/my_books/get_lists", "session_id", sessionID),
        success: function (result) {
            $(".navigation ul li:not('.template') a").remove();
            let length = Object.keys(result).length;
            for (let i = 0; i < length; i++) {
                let item = $(".navigation ul li.template").clone().removeClass("template");
                $(item).find("a").html(result[i]["name"]);
                $(item).appendTo(".navigation ul");
                $(item).data("id", result[i]["id"])
            }
            assignReadingListNavigationHandlers();
            $(".navigation ul li").children().eq(1).trigger("click");
        },
        error: function (jqXHR) {
            if (jqXHR.status == 403) {
                sessionExpired();
            }
            console.log(jqXHR.status + " " + jqXHR.responseText);
        }
    });
    $(".container .entries .edit-lists button.create-list").off("click"); // Remove any preexisting handlers to prevent duplicate results
    $(".container .entries .edit-lists button.create-list").click(function () {
        $(this).hide();
        $(".container .entries .edit-lists .add-container").removeClass("hidden");
    });
    $(".container .entries .edit-lists form").off("submit"); // Remove any prexisting handlers to prevent duplicate results
    $(".container .entries .edit-lists form").on("submit", function (event) {
        event.preventDefault();
        $.ajax({
            type: "POST",
            url: "/cgi-bin/my_books/create_list",
            data: JSON.stringify({
                "session_id": sessionID,
                "list_name": $(".container .entries .edit-lists form input[name=list-name]").val()
            }),
            success: function () {
                loadMyBooks();
                $(".container .entries .edit-lists form input[name=list-name]").val("");
                // Remove the entered string incase it is re-entered before page refresh.
                $(".container .entries .edit-lists .add-container").addClass("hidden");
                $(".container .entries .edit-lists button.create-list").show();
            },
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
                console.log(jqXHR.status + " " + jqXHR.responseText);
            }
        });
    });
}

function assignReadingListNavigationHandlers () {
    $(".navigation ul li a").off("click");
    $(".navigation ul li a").click(function () {
        $(".navigation ul li a.active").removeClass("active")
        $(this).addClass("active");
        let listName = $(this).html();

        let requestURL = "/cgi-bin/my_books/get_list_entries";
        requestURL = addGetParameter(requestURL, "session_id", sessionID)
        requestURL = addGetParameter(requestURL, "list_id", $(this).closest("li").data("id"))
        $.ajax({
            type: "GET",
            url: requestURL,
            success: function (result) {
                if (["Currently Reading", "Want to Read", "Have Read"].includes(listName)) {
                    $(".container .entries .edit-lists button.delete-list").hide(); // Ensure that permanent lists
                    // cannot be deleted
                } else {
                    $(".container .entries .edit-lists button.delete-list").show();
                }
                $(".container .entries .book:not('.template')").remove();
                // Remove existing entries so only new ones are shown.

                if (result["button"]) {
                    $(".container .entries .book.template .actions .read").show()
                    // incase it was hidden by previous action
                    $(".container .entries .book.template .actions .read .reading-list-manipulation").html(result["button"])
                } else {
                    $(".container .entries .book.template .actions .read").hide()
                }

                let books = result["books"];
                console.log(Object.keys(books).length);
                for (let i = 0; i < Object.keys(books).length; i++) {
                    let averageRating = books[i]["average_rating"];
                    let template = $(".container .entries .book.template").clone().removeClass("template");
                    $(template).find(".title").html(books[i]["title"]);
                    let author = $(template).find(".author");
                    $(author).html(books[i]["author"]);
                    $(author).data("id", books[i]["author_id"]);
                    $(template).find(".date-added").html(books[i]["date_added"]);
                    $(template).find(".synopsis").html(books[i]["synopsis"]);
                    $(template).find(".about-review .average-review").html(averageRating.toFixed(1));
                    $(template).find(".about-review span.num-review").html(books[i]["num_reviews"]);
                    $(template).find(".cover img").attr("src", books[i]["cover"]);

                    changeElemStars($(template).find(".rating-container i"), averageRating);

                    let genres = $(template).find("ol");
                    for (let k in books[i]["genres"]) {
                        let item = $(genres).find("li.template").clone().removeClass("template");
                        $(item).find("a").html(books[i]["genres"][k]);
                        $(item).appendTo(genres);
                    }

                    $(template).insertBefore(".edit-lists");
                    $(template).data("id", books[i]["id"]);

                    let newURI = ("#" + listName).toTitleCase().split(" ").join("");
                    // Convert Name to title case, then remove ALL spaces
                    // which is why .replace is not used, and add a hashtag to
                    // use a bookmark in the search bar.
                    history.pushState({urlPath: newURI},"", newURI);
                }
                assignGenreNavigationHandlers(); // Assign handlers for the genre buttons once they have loaded
                // Handlers are not kept by the clone for whatever reason.
                assignBookNavigationHandlers();
                assignAuthorNavigationHandlers();
                assignDeleteHandlers(listName); // Assign delete handlers to remove entries
                assignMovementHandlers(listName, result["move_target_id"]);
                assignListDeleteHandlers(listName); // Slower, but avoids the difficulty and possible cost of finding the list Name again.
            },
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
                console.log(jqXHR.status + " " + jqXHR.responseText);
            }
        });
    });
}

function assignListDeleteHandlers (listName) {
    $(".container .entries .edit-lists button.delete-list").off("click"); // Remove
    $(".container .entries .edit-lists button.delete-list").click(function () {
        $.ajax({
            type: "POST",
            url: "/cgi-bin/my_books/remove_list",
            data: JSON.stringify({
                "session_id": sessionID,
                "list_id": $(".container .navigation li a.active").parent().data("id") // ID is attached to li element
            }),
            success: loadMyBooks, // Get the new list names, and move back to the first list and get content
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
                console.log(jqXHR.status + " " + jqXHR.responseText);
            }
        });
    });
}

function assignDeleteHandlers (listName) {
    $(".container .entries .book button.delete").off("click");
    $(".container .entries .book button.delete").click(function () {
        let book = $(this).closest("div.book");
        $.ajax({
            type: "POST",
            url: "/cgi-bin/my_books/remove_list_entry",
            data: JSON.stringify({
                "list_id": $(".container .navigation li a.active").parent().data("id"),
                "book_id": $(book).data("id"),
                "session_id": sessionID
            }),
            success: function (result) {
                $(book).fadeOut(500); // Hide the entry from the list
            },
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
                console.log(jqXHR.status + " " + jqXHR.responseText);
            }
        });
    });
}

function assignMovementHandlers (listName, id) {
    $(".container .entries .book button.read").off("click");
    $(".container .entries .book button.read").data("target_id", id);
    $(".container .entries .book button.read").click(function () {
        let book = $(this).closest("div.book");
        $.ajax({
            type: "POST",
            url: "/cgi-bin/my_books/move_list_entry",
            data: JSON.stringify({
                "list_id": $(".container .navigation li a.active").parent().data("id"),
                "book_id": $(book).data("id"),
                "target_list_id": $(this).data("target_id"),
                "session_id": sessionID
            }),
            success: function (result) {
                $(book).fadeOut(500); // Hide the entry from the list
            },
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
                console.log(jqXHR.status + " " + jqXHR.responseText);
            }
        });
    });
}

// -----------------------------------------------------------------------------
// Genres
// -----------------------------------------------------------------------------
function assignGenreNavigationHandlers () {
    $(".genre-button").off("click");
    $(".genre-button").click(function (event) {
        switchGenrePage($(this).html());
    });
}

function switchGenrePage (genre) {
    $.ajax({
        type: "GET",
        url: addGetParameter("/cgi-bin/genres/about_data", "genre_name", genre),
        success: function (result) {
            changePageContent("/html/genre.html", false); // Must be synchronous, otherwise subsequent
            // population of the template the request supplies may fail, as it may not arrive in time.
            
            changeActiveLink(null, "Browse"); // Change page to browse page

            $(".genre-name").html(result["name"]);
            $(".about").html(result["about"]);
            let books = result["books"];
            for (let i = 0; i < Object.keys(books).length; i++) {
                let item = $(".book-summary.template").clone().removeClass("template");
                $(item).find(".title").html(books[i]["title"]);
                $(item).find(".author").html(books[i]["author"]);
                $(item).find("img").attr("src", books[i]["cover"]);
                $(item).appendTo(".genre-book-items");
                $(item).data("id", books[i]["id"]);
            }
            assignBookNavigationHandlers(); // Assign navigation for the book summaries.
        },
        error: function (jqXHR) {
            $("main").html(jqXHR.responseText); // Fills in the main body with 404 error message
        },
        complete: function () {
            changePageURI("genre/" + genre); // Update page URL to point to the new genre and allow for refreshing
            // Last as it is least likely to be seen, so appears smoother
        }
    });
}

// -----------------------------------------------------------------------------
// Book pages
// -----------------------------------------------------------------------------
function assignBookNavigationHandlers () {
    // If the link is an entire div, with an image, title etc, it needs to navigate down the DOM to find the title
    $(".book-button").off("click");
    $(".book-button").click(function () {
        let bookID = $(this).closest(".book").data("id");
        if (!bookID) { // If the previous attempt is undefined, this runs, and it must be this, if the previous is
            // undefined
            bookID = $(this).closest(".book-summary").data("id");
        }
        switchBookPage(bookID);
    });
}

function changeNumVisibleSimilarBooks () {
    if (currentPage == "Book") {
        let summaries = $(".similar-books .book-summary");
        let windowWidth = $(".similar-books").width();
        let summaryWidth = 250;
        let num = Math.floor(windowWidth / summaryWidth) * 2; // Gets number of summaries to show
        $(summaries).addClass("hidden");
        for (let i = 0; i <= num; i++) { // For some reason, i < num shows 1 too few. Clearly not starting from 0.
            $(summaries).eq(i).removeClass("hidden")
        }
    }
}
$(window).resize($.debounce(300, changeNumVisibleSimilarBooks));

function switchBookPage (bookID) {
    let request_url = addGetParameter("/cgi-bin/books/about_data", "book_id", bookID);
    request_url = addGetParameter(request_url, "session_id", sessionID);
    $.ajax({
        type: "GET",
        url: request_url,
        success: function (result) {
            changePageContent("/html/book.html", false); // Must be synchronous, otherwise subsequent
            // population of the template the request supplies may fail, as it may not arrive in time.

            changeActiveLink(null, "Browse");

            let url = addGetParameter("/cgi-bin/my_books/get_lists_book_target", "session_id", sessionID);
            url = addGetParameter(url, "book_id", bookID);
            $.ajax({
                type: "GET",
                url: url,
                success: function (result) {
                    for (let i = 0; i < Object.keys(result).length; i++) {
                        let item = $(".reading-list-selection ul li.template").clone().removeClass("template");
                        $(item).find(".list-name").html(result[i]["list_name"]);
                        if (result[i]["has_book"]) {
                            $(item).find("button").addClass("inactive");
                            $(item).find("i.status").addClass("fa fa-check-circle");
                        } else {
                            $(item).find("i.status").addClass("fa fa-circle");
                        }
                        $(item).data("id", result[i]["id"]);
                        $(item).appendTo(".reading-list-selection ul");
                    }
                },
                error: function (jqXHR) {
                    if (jqXHR.status == 403) {
                        sessionExpired();
                    }
                    console.log(jqXHR.status + " " + jqXHR.responseText);
                },
                complete: function () {
                    assignChangeReadingListHandler(bookID); // Needs to be here as this request is asynchronous
                    // Needs to be under complete, as it needs to run even on failure.
                }
            });

            $(".book-about .title").html(result["title"]);
            $(".book-about .synopsis").html(result["synopsis"]);
            $(".book-about img.cover").attr("src", result["cover_image"]);
            $(".book-about .isbn").html(result["isbn"]);
            $(".book-about .publish-date").html(result["release_date"]);

            let genres = result["genres"]
            for (let i = 0; i < Object.keys(genres).length; i++) {
                $(".book-about .genres li.template a").html(genres[i]);
                $(".book-about .genres li.template").clone().removeClass("template").appendTo(".book-about .genres ol");
            }

            let numWantRead = result["num_want_read"];
            if (numWantRead == 1) {
                $(".book-about .book-stats .num-want-read .person-qualifier").html("person");
            }
            let numReading = result["num_reading"];
            if (numReading == 1) {
                $(".book-about .book-stats .num-reading .person-qualifier").html("person");
            }
            let numRead = result["num_read"];
            if (numRead == 1) {
                $(".book-about .book-stats .num-read .person-qualifier").html("person has");
            } // Other option is the default as it is hardcoded in the HTML
            $(".book-about .book-stats .num-want-read .value").html(numWantRead);
            $(".book-about .book-stats .num-reading .value").html(numReading);
            $(".book-about .book-stats .num-read .value").html(numRead);

            let author = $(".book-about .author");
            $(author).html(result["author"]);
            $(author).data("id", result["author_id"])

            if (result["author_following"]) {
                $(".book-about .author-about .follow-author").addClass("hidden");
                $(".book-about .author-about .unfollow-author").removeClass("hidden");
            } else {
                $(".book-about .author-about .unfollow-author").addClass("hidden");
                $(".book-about .author-about .follow-author").removeClass("hidden");
            }

            $(".book-about .author-about .num-followers").html(result["author_number_followers"]); // Keep in here
            // rather than use the other function to help reduce the amount requests the client sends, and reduce
            // server load, and send the number as a response to the follow/unfollow request
            $(".book-about .author-about .about").html(result["author_about"]);

            let similarBooks = result["similar_books"];
            for (let i = 0; i < Object.keys(similarBooks).length; i++) {
                let template = $(".book-about .similar-books .book-summary.template").clone().removeClass("template");
                $(template).find("img").attr("src", similarBooks[i]["cover"]);
                $(template).find(".title").html(similarBooks[i]["title"]);
                $(template).find(".author").html(similarBooks[i]["author"]);
                $(template).appendTo(".book-about .similar-books");
                $(template).data("id", similarBooks[i]["book_id"]);
            }

            $(".book-about .average-review").html(result["average_rating"]);
            changeElemStars($(".book-about .top-container .rating i"), result["average_rating"]);
            changeElemStars($(".book-about .reviews .average-review-container i"), result["average_rating"]);
            let numRatings = result["num_ratings"];
            $(".book-about .num-review").html(numRatings);
            $(".book-about .review-distribution .bar#5-star .number").html(result["num_5_stars"]);
            $(".book-about .review-distribution .bar#4-star .number").html(result["num_4_stars"]);
            $(".book-about .review-distribution .bar#3-star .number").html(result["num_3_stars"]);
            $(".book-about .review-distribution .bar#2-star .number").html(result["num_2_stars"]);
            $(".book-about .review-distribution .bar#1-star .number").html(result["num_1_star"]);

            numRatings = Math.max(numRatings, 1); // If numRatings is 0, it changes it to 1, which does not affect the
            // percentages but avoids 0 division errors.
            let percentage = ((result["num_5_stars"] / numRatings) * 100)
            $(".book-about .review-distribution .bar#5-star .percentage").html(percentage.toFixed(2));
            $(".book-about .review-distribution .bar#5-star meter").val(percentage);
            percentage = ((result["num_4_stars"] / numRatings) * 100)
            $(".book-about .review-distribution .bar#4-star .percentage").html(percentage.toFixed(2));
            $(".book-about .review-distribution .bar#4-star meter").val(percentage);
            percentage = ((result["num_3_stars"] / numRatings) * 100)
            $(".book-about .review-distribution .bar#3-star .percentage").html(percentage.toFixed(2));
            $(".book-about .review-distribution .bar#3-star meter").val(percentage);
            percentage = ((result["num_2_stars"] / numRatings) * 100)
            $(".book-about .review-distribution .bar#2-star .percentage").html(percentage.toFixed(2));
            $(".book-about .review-distribution .bar#2-star meter").val(percentage);
            percentage = ((result["num_1_star"] / numRatings) * 100)
            $(".book-about .review-distribution .bar#1-star .percentage").html(percentage.toFixed(2));
            $(".book-about .review-distribution .bar#1-star meter").val(percentage);

            $(".book-about a.purchase_link").attr("href", result["purchase_link"])

            let reviews = result["reviews"];
            for (let i = 0; i < Object.keys(reviews).length; i++) {
                let template = $(".book-about .user-reviews .review.template").clone().removeClass("template");
                $(template).data("id", reviews[i]["id"]);
                $(template).find(".username").html(reviews[i]["username"]);
                $(template).find(".date").html(reviews[i]["date_added"]);
                if (reviews[i]["summary"] == null) {
                    $(template).find(".summary").addClass("hidden");
                } else {
                    $(template).find(".summary").removeClass("hidden");
                    $(template).find(".summary").html(reviews[i]["summary"]);
                }
                if (reviews[i]["rating_body"] == null) {
                    $(template).find(".review-body").addClass("hidden");
                } else {
                    $(template).find(".review-body").removeClass("hidden");
                    $(template).find(".review-body").html(reviews[i]["rating_body"]);
                }

                changeElemStars($(template).find(".overall-rating i"), reviews[i]["overall_rating"]);
                if (reviews[i]["plot_rating"] == null) {
                    $(template).find(".plot-rating").addClass("hidden");
                } else {
                    $(template).find(".plot-rating").removeClass("hidden");
                    changeElemStars($(template).find(".plot-rating i"), reviews[i]["plot_rating"]);
                }
                if (reviews[i]["character_rating"] == null) {
                    $(template).find(".character-rating").addClass("hidden");
                } else {
                    $(template).find(".character-rating").removeClass("hidden");
                    changeElemStars($(template).find("character-rating i"), reviews[i]["character_rating"]);
                }
                $(template).appendTo(".book-about .user-reviews");
            }

            $(".book-about .user-review").data("list_id", result["list_id"]);
            let currentUserReview = result["current_user_review"];
            if (currentUserReview != null) {
                let existingReview = $(".book-about .user-review .existing-review").removeClass("hidden");
                $(existingReview).data("id", currentUserReview["review_id"]);
                $(".book-about .user-review .leave-review").addClass("hidden");
                if (currentUserReview["overall_rating"] == null) {
                    $(existingReview).find(".overall-rating").addClass("hidden");
                } else {
                    $(existingReview).find(".overall-rating").removeClass("hidden");
                    changeElemStars(
                        $(existingReview).find(".overall-rating i"),
                        currentUserReview["overall_rating"]
                    );
                }
                if (currentUserReview["plot_rating"] == null) {
                    $(existingReview).find(".plot-rating").addClass("hidden");
                } else {
                    $(existingReview).find(".plot-rating").removeClass("hidden");
                    changeElemStars($(existingReview).find(".plot-rating i"), currentUserReview["plot_rating"]);
                }
                if (currentUserReview["character_rating"] == null) {
                    $(existingReview).find(".character-rating").addClass("hidden");
                } else {
                    $(existingReview).find(".character-rating").removeClass("hidden");
                    changeElemStars(
                        $(existingReview).find(".character-rating i"),
                        currentUserReview["character_rating"]
                    );
                }

                if (currentUserReview["summary"] == null) {
                    $(existingReview).find(".rating-summary").addClass("hidden");
                } else {
                    $(existingReview).find(".rating-summary").removeClass("hidden");
                    $(existingReview).find(".rating-summary").html(currentUserReview["summary"]);
                }
                if (currentUserReview["rating_body"] == null) {
                    $(existingReview).find(".review-body").addClass("hidden");
                } else {
                    $(existingReview).find(".review-body").removeClass("hidden");
                    $(existingReview).find(".review-body").html(currentUserReview["rating_body"]);
                }
            }

            assignReviewDeleteButtonHandler();
            assignAuthorFollowHandlers();
            assignGenreNavigationHandlers(); // Genre navigation handlers need to be reassigned as there will be new ones
            // added
            assignAuthorNavigationHandlers();
            assignReviewSubmissionHandlers(bookID);
            currentPage = "Book";
            changeNumVisibleSimilarBooks();
            assignBookNavigationHandlers();
        },
        error: function (jqXHR) {
            if (jqXHR.status == 403) {
                sessionExpired();
            }
            $("main").html(jqXHR.responseText); // Fills in the main body with 404 error message
        },
        complete: function () {
            changePageURI("book/" + bookID); // Update page URL to point to the new genre and allow for refreshing
            // Last as it is least likely to be seen, so appears smoother
        }
    });
}

function assignReviewDeleteButtonHandler () {
    $(".book-about .existing-review button.delete-review").click(function () {
        $(".book-about .user-review .leave-review").removeClass("hidden");
        let existingReview = $(".book-about .user-review .existing-review");
        $(existingReview).addClass("hidden"); // Do this before making the request, so it
        // can continue in the background for appeared responsiveness.
        $.ajax({
            type: "POST",
            url: "/cgi-bin/books/delete_review",
            data: JSON.stringify({
                "session_id": sessionID,
                "review_id": $(existingReview).data("id")
            }), // The user can only have one review of the book
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
            },
            complete: reloadCurrentPage // Avoids the stars not updating.
        }); // The response does not matter
    });
}

function assignChangeReadingListHandler (bookID) {
    $(".book-about button.add-list").click(function () {
        if (sessionID) {
            $(".reading-list-selection").removeClass("hidden");
        } else {
            showSignInPopup();
        }
    });
    $(".reading-list-selection ul li button:not('.inactive')").click(function () {
        let list_id = $(this).closest("li").data("id");
        $.ajax({
            type: "POST",
            url: "/cgi-bin/my_books/add_list_entry",
            data: JSON.stringify({
                "list_id": list_id,
                "session_id": sessionID,
                "book_id": bookID
            }),
            success: function () {
                reloadCurrentPage();
            },
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
            },
            complete: function () {
                hideReadingListPopup();
            }
        });
    });
}

function hideReadingListPopup () {
    $(".reading-list-selection").addClass("hidden");
}

$(window).click(function (event) {
    if ($(".reading-list-selection")[0] == event.target) {
        hideReadingListPopup();
    }
});

function assignAuthorFollowHandlers () {
    $(".author-about .follow-author").click(function () {
        // Can only follow a user if an account is known, so prompts if not signed in.
        if (sessionID) {
            $.ajax({
                type: "POST",
                url: "/cgi-bin/authors/follow_author",
                data: JSON.stringify({
                    "session_id": sessionID,
                    "author_id": $(".author").data("id")
                }),
                success: function (result) {
                    $(".author-about .follow-author").addClass("hidden");
                    $(".author-about .unfollow-author").removeClass("hidden");
                    $(".author-about .num-followers").html(result); // Update number of followers
                },
                error: function (jqXHR) {
                    if (jqXHR.status == 403) {
                        sessionExpired();
                    }
                }
            });
        } else {
            showSignInPopup();
        }
    });
    $(".author-about .unfollow-author").click(function () {
        $.ajax({ // This cannot be shown if not signed in, so does not check
            type: "POST",
            url: "/cgi-bin/authors/unfollow_author",
            data: JSON.stringify({
                "session_id": sessionID,
                "author_id": $(".author").data("id")
            }),
            success: function (result) {
                $(".author-about .follow-author").removeClass("hidden");
                $(".author-about .unfollow-author").addClass("hidden");
                $(".author-about .num-followers").html(result); // Update number of followers
            },
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
            }
        });
    });
}

function assignStarRatingEntryButtonHandlers (container) {
    $(container).data("rating", null); // Ensure that the rating is null if it is not
    // changed.
    $(container).find("button").click(function (event) {
        event.preventDefault(); // Prevent button submitting form
        let buttons = $(this).closest(".rating-entry-container").find("button");
        $(buttons).removeClass("highlight");
        let reviewNum = $(this).index() + 1; // This is indexed from 0, so needs to be incremented by 1.
        for (let i = 0; i < reviewNum; i++) {
            $(buttons).eq(i).addClass("highlight"); // eq gets the nth object from the selector
        }
        $(this).closest(".rating-entry-container").data("rating", reviewNum); // Change the stored review.
    });
}

function assignReviewSubmissionHandlers (bookID) {
    assignStarRatingEntryButtonHandlers($(".leave-review .rating-entry-container"));
    $(".leave-review form").on("submit", function (event) {
        event.preventDefault();
        // 'Assertion failed: Input argeument is not an HTMLInputElement' error is coming from LastPass.
        if (sessionID) {
            let overallRating = $(".leave-review .overall-rating-entry .rating-entry-container").data("rating");
            let summary = $(".leave-review input[name=summary]").val();
            let thoughts = $(".leave-review textarea").val();
            if (summary == "") {
                summary = null; // It must be null for the server it is left empty
            }
            if (thoughts == "") {
                thoughts = null;
            }
            if (overallRating == null) {
                reviewSubmissionAlert("Overall rating cannot be blank.")
            } else if ((summary == null) && thoughts) {
                reviewSubmissionAlert("A summary must be present if you have given your thoughts and feelings.")
            } else {
                $.ajax({
                    type: "POST",
                    url: "/cgi-bin/books/add_review",
                    data: JSON.stringify({
                        "session_id": sessionID,
                        "book_id": bookID,
                        "overall_rating": overallRating,
                        "plot_rating": $(".leave-review .plot-rating-entry .rating-entry-container").data("rating"),
                        "character_rating": $(".leave-review .character-rating-entry .rating-entry-container").data("rating"),
                        "summary": summary,
                        "thoughts": thoughts
                    }),
                    success: function () {
                        reloadCurrentPage(); // Just reloads the page
                    },
                    error: function () {
                        if (jqXHR.status == 403) {
                            sessionExpired();
                        } else {
                            reviewSubmissionAlert("Something went wrong.");
                        }
                        console.log(jqXHR.status + " " + jqXHR.responseText);
                    }
                });
            }
        } else {
            showSignInPopup();
        }
    });
}

function reviewSubmissionAlert (message) {
    let alert = $(".leave-review .alert");
    $(alert).html(message);
    $(alert).show();
    timeout = setTimeout(function () {
        $(alert).fadeOut(500); // Fade out in 1/2 seconds
    }, 8000); // Hide alert after 8 seconds
}

// -----------------------------------------------------------------------------
// Rating stars
// -----------------------------------------------------------------------------
function changeElemStars (icons, averageRating) {
    let numFull = Math.trunc(averageRating);
    for (let i = 0; i < numFull; i++) {
        $(icons[i]).removeClass().addClass("fa fa-star"); // Removes all classes first. This is easier
        // as it then does not need to worry about removing the two other possibilities. Does mean
        // fa needs to be added as well
    }
    if (numFull != averageRating) {
        $(icons[numFull]).removeClass().addClass("fa fa-star-half-o");
        numFull += 1;
    }
    for (let i = numFull; i < 5; i++) {
        $(icons[i]).removeClass().addClass("fa fa-star-o");
    }
}

// -----------------------------------------------------------------------------
// Authors
// -----------------------------------------------------------------------------
function switchAuthorPage (authorID) {
    $.ajax({
        type: "GET",
        url: addGetParameter("/cgi-bin/authors/about_data", "author_id", authorID),
        success: function (result) {
            changePageContent("/html/author.html", false);  // Must be synchronous, otherwise subsequent
            // population of the template the request supplies may fail, as it may not arrive in time.
            changeActiveLink(null, "Browse"); // Change page to browse page
            $(".name h1").html(result["name"]);
            $(".about").html(result["about"]);
            $(".author").data("id", result["author_id"]);
            $(".num-followers").html(result["num_followers"]);
            let books = result["books"];
            for (let i = 0; i < Object.keys(books).length; i++) {
                let summary = $(".book-summary.template").clone().removeClass("template");
                $(summary).find(".title").html(books[i]["title"]);
                $(summary).find(".author").html(result["name"]);
                $(summary).find("img").attr("src", books[i]["cover"]);
                $(summary).data("id", books[i]["id"]);
                $(summary).appendTo(".author-book-items");
            }

            $(".author-rating-container .about-review .average-review").html(result["average_rating"]);
            $(".author-rating-container .about-review .num-review").html(result["num_ratings"]);
            changeElemStars($(".author-rating-container .rating i"), result["average_rating"]);

            let genres = result["genres"];
            for (let i = 0; i < Object.keys(genres).length; i++) {
                let template = $(".author-genre-items .template").clone().removeClass("template");
                $(template).find(".genre-button").html(genres[i]);
                $(template).appendTo(".author-genre-items ol");
            }

            assignAuthorFollowHandlers();
            assignBookNavigationHandlers();
            assignGenreNavigationHandlers();
        },
        error: function (jqXHR) {
            $("main").html(jqXHR.responseText); // Fills in the main body with 404 error message
        },
        complete: function () {
            changePageURI("author/" + authorID); // Update page URL to point to the new genre and allow for refreshing
            // Last as it is least likely to be seen, so appears smoother
        }
    });
}

function assignAuthorNavigationHandlers () {
    $("a.author").off("click");
    $("a.author").click(function (event) {
        switchAuthorPage($(this).data("id"));
    });
}

// -----------------------------------------------------------------------------
// Diary entries
// -----------------------------------------------------------------------------
function loadDiary () {
    $.ajax({
        type: "GET",
        url: addGetParameter("/cgi-bin/diary/get_entries", "session_id", sessionID),
        success: function (result) {
            let entries = result["entries"];
            for (let i = 0; i < Object.keys(entries).length; i++) {
                let book = entries[i];
                let template = $(".entries .diary-entry.template").clone().removeClass("template");
                $(template).find(".cover img").attr("src", book["cover_image"]);
                $(template).find(".book").html(book["title"]);
                $(template).find(".book").data("id", book["book_id"]);
                $(template).find(".author").html(book["author_name"]);
                $(template).find(".author").data("id", book["author_id"]);
                changeElemStars($(template).find(".rating-container .rating i"), book["average_rating"]);
                $(template).find(".rating-container .average-review").html(book["average_rating"]);
                $(template).find(".rating-container .num-review").html(book["number_ratings"]);
                if (book["overall_rating"] != null) {
                    changeElemStars($(template).find(".ratings .overall-rating i"), book["overall_rating"]);
                } else {
                    $(template).find(".ratings .overall-rating").hide();
                }
                if (book["plot_rating"] != null) {
                    changeElemStars($(template).find(".ratings .plot-rating i"), book["plot_rating"]);
                } else {
                    $(template).find(".ratings .plot-rating").hide();
                }
                if (book["character_rating"] != null) {
                    changeElemStars($(template).find(".ratings .character-rating i"), book["character_rating"]);
                } else {
                    $(template).find(".ratings .character-rating").hide();
                }
                if (book["summary"] != null) {
                    $(template).find(".summary").html(book["summary"]);
                } else {
                    $(template).find(".summary").hide();
                }
                if (book["thoughts"] != null) {
                    $(template).find(".thoughts").html(book["thoughts"]);
                } else {
                    $(template).find(".thoughts").hide();
                }
                $(template).find(".book-info .date-added").html(book["date_added"]);
                $(template).find(".book-info .num-pages-read").html(book["pages_read"]);
                $(template).data("id", book["entry_id"])
                $(template).appendTo(".entries");
            }

            let books = result["books"];
            for (let i = 0; i < Object.keys(books).length; i++) {
                let book = books[i];
                let template = $(".new-diary-entry select option.template").clone().removeClass("template");
                $(template).text(book["title"]);
                $(template).val(book["book_id"]);
                $(template).insertBefore(".new-diary-entry select option.template");
            }
            // $(".new-diary-entry select option.template").remove() // The template needs to be removed before any value
            // is shown as default
            assignDeleteDiaryEntryButton(); // This is more important, so is done first for speed.
            $(".entry-management .new-entry").click(function () {
                $(".new-diary-entry").removeClass("hidden"); // Show form on click
            });

            $(".new-diary-entry form input[name=complete]").click(function () {
                let form = $(".new-diary-entry form");
                let label = $(form).find("input[name=review]").closest("label");
                if (Boolean($(form).find("input[name=complete]:checked").val())) {
                    $(label).removeClass("hidden")
                } else {
                    $(label).addClass("hidden");
                    $(form).find("input[name=review]").prop("checked", false); // Unselect publish as review button
                    // so that if the user clicks on complete, then review, then unselects complete, it is NOT 
                    // published as a review.
                }
            });

            assignDiaryEntrySubmissionHandlers();
            assignBookNavigationHandlers();
            assignAuthorNavigationHandlers();
        },
        error: function (jqXHR) {
            if (jqXHR.status == 403) {
                sessionExpired();
            }
            console.log(jqXHR.status + " " + jqXHR.responseText);
        }
    });
}

function assignDeleteDiaryEntryButton () {
    $(".diary-entry .delete").click(function () {
        let entry = $(this).closest(".diary-entry");
        $.ajax({
            type: "POST",
            url: "cgi-bin/diary/delete_entry",
            data: JSON.stringify({
                "session_id": sessionID,
                "entry_id": $(entry).data("id")
            }),
            success: function (result) {
                $(entry).fadeOut(500); // Hide the entry from the list
            },
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
                console.log(jqXHR.status + " " + jqXHR.responseText);
            }
        });
    });
}

function assignDiaryEntrySubmissionHandlers () {
    assignStarRatingEntryButtonHandlers($(".new-diary-entry .new-entry .rating-entry-container"));
    $(".new-diary-entry form.new-entry").on("submit", function () {
        event.preventDefault(); // Prevent reload and sending of params via get
        // Do not need to check for a user being logged in - they cannot reach this point without signing in
        let form = $(".new-diary-entry form.new-entry");
        let overallRating = $(form).find(".overall-rating-entry .rating-entry-container").data("rating");
        let summary = $(form).find("input[name=summary]").val();
        let thoughts = $(form).find("textarea").val();
        let pagesRead = $(form).find("input[name=pages-read]").val();
        let bookID = $(form).find("select").val();
        let completed = Boolean($(form).find("input[name=complete]:checked").val());
        let asReview = Boolean($(form).find("input[name=review]:checked").val());

        if (summary == "") {
            summary = null; // It must be null for the server it is left empty
        }
        if (thoughts == "") {
            thoughts = null;
        }
        if (overallRating == null) {
            diaryEntrySubmissionAlert("Overall rating cannot be blank.")
        } else if ((summary == null) && thoughts) {
            diaryEntrySubmissionAlert("A summary must be present if you have given your thoughts and feelings.")
        } else if (pagesRead == "") {
            diaryEntrySubmissionAlert("Pages read cannot be blank");
        } else if (bookID == null) {
            diaryEntrySubmissionAlert("Please select a book");
        } else {
            $.ajax({
                type: "POST",
                url: "/cgi-bin/diary/add_entry",
                data: JSON.stringify({
                    "session_id": sessionID,
                    "book_id": bookID,
                    "overall_rating": overallRating,
                    "plot_rating": $(form).find(".plot-rating-entry .rating-entry-container").data("rating"),
                    "character_rating": $(form).find(".character-rating-entry .rating-entry-container").data("rating"),
                    "pages_read": pagesRead,
                    "summary": summary,
                    "thoughts": thoughts,
                    "book_completed": completed,
                    "as_review": asReview
                }),
                success: function () {
                    reloadCurrentPage(); // Just reloads the page
                },
                error: function () {
                    if (jqXHR.status == 403) {
                        sessionExpired();
                    } else {
                        diaryEntrySubmissionAlert("Something went wrong.");
                    }
                    console.log(jqXHR.status + " " + jqXHR.responseText);
                }
            });
        }
    });
}

function diaryEntrySubmissionAlert (message) {
    let alert = $(".new-diary-entry .alert");
    $(alert).html(message);
    $(alert).show();
    timeout = setTimeout(function () {
        $(alert).fadeOut(500); // Fade out in 1/2 seconds
    }, 8000); // Hide alert after 8 seconds
}

function hideDiaryEntryPopup () {
    $(".new-diary-entry").addClass("hidden");
}

$(window).click(function (event) {
    if ($(".new-diary-entry")[0] == event.target) {
        hideDiaryEntryPopup(); // Close
    }
});

// -----------------------------------------------------------------------------
// Home page
// -----------------------------------------------------------------------------
function addHomePageDetails (json, divID) {
    for (let i = 0; i < Object.keys(json).length; i++) {
        let summary = $(".book-summary.template").clone().removeClass("template");
        $(summary).find("img").attr("src", json[i]["cover"]);
        $(summary).find(".author").html(json[i]["author"]);
        $(summary).find(".title").html(json[i]["title"]);
        $(summary).data("id", json[i]["book_id"]);
        $(summary).appendTo(".row#" + divID + " .books");
    }
}

function loadHomePage () {
    $.ajax({
        type: "GET",
        url: addGetParameter("/cgi-bin/home/get_data", "session_id", sessionID),
        success: function (result) {
            addHomePageDetails(result["trending"], "trending");
            addHomePageDetails(result["newest_additions"], "newest");
            
            let currentlyReading = result["currently_reading"];
            if (currentlyReading == null) { // Will only be null if there is no user, so all user specifics can
                // be hidden.
                $(".row#reading").addClass("hidden"); // Remove so the hr disappears. These will reappear on sign in
            } else if (currentlyReading.length == 0) {
                $(".row#reading").addClass("hidden");
            } else {
                $(".row#reading").removeClass("hidden");
                addHomePageDetails(currentlyReading, "reading");
            }

            let wantRead = result["want_read"];
            if (wantRead == null) { // Will only be null if there is no user, so all user specifics can
                // be hidden.
                $(".row#want-read").addClass("hidden"); // Remove so the hr disappears. These will reappear on sign in
            } else if (wantRead.length == 0) {
                $(".row#want-read").addClass("hidden");
            } else {
                $(".row#want-read").removeClass("hidden");
                addHomePageDetails(wantRead, "want-read");
            }

            let recommended = result["recommended"];
            if (recommended == null) { // Will only be null if there is no user, so all user specifics can
                // be hidden.
                $(".row#recommended").addClass("hidden"); // Remove so the hr disappears. These will reappear on sign in
            } else if (recommended.length == 0) {
                $(".row#recommended").addClass("hidden");
            } else {
                $(".row#recommended").removeClass("hidden");
                addHomePageDetails(recommended, "recommended");
            }

            changeNumVisibleSummaries(); // Needs to run once, as resize will not trigger by this point
            assignBookNavigationHandlers();
        },
        error: function (jqXHR) {
            if (jqXHR.status == 403) {
                sessionExpired();
            }
            console.log(jqXHR.status + " " + jqXHR.responseText);
        }
    });
}

function changeNumVisibleSummaries () {
    if (currentPage == "Home" || currentPage == "Browse") {
        let summaries = $(".row .book-summary");
        let windowWidth = $(".row:not('.hidden')").width(); // Must be not hidden, otherwise it can give 0, if the div is hidden.
        let summaryWidth = 250;
        let num = Math.floor(windowWidth / summaryWidth); // Gets number of summaries to show
        $(summaries).addClass("hidden");
        $(".row").each(function () {
            let summaries = $(this).find(".book-summary");
            for (let i = 0; i < num; i++) {
                $(summaries).eq(i).removeClass("hidden");
            }
        });
    }
}

$(window).resize($.debounce(300, changeNumVisibleSummaries));  // Runs every 300ms. Reduces load as this will run
// frequently

// -----------------------------------------------------------------------------
// Recommendation page
// -----------------------------------------------------------------------------
function loadRecommendationsPage () {
    $.ajax({
        type: "GET",
        url: addGetParameter("/cgi-bin/recommendations/get_recommendations", "session_id", sessionID),
        success: function (result) {
            let iterateLength = Object.keys(result["data"]).length
            if (!result["new_user"]) {
                $(".initial-preference").addClass("hidden");
                $(".recommendation-entries").removeClass("hidden");
                for (let i = 0; i < iterateLength; i++) {
                    let recommendation = result["data"][i];
                    let template = $(".recommendation-entries .book.template").clone().removeClass("template");

                    $(template).find(".cover img").attr("src", recommendation["cover_image"]);

                    $(template).find(".title-container a.title").html(recommendation["title"]);
                    $(template).data("id", recommendation["book_id"]);

                    $(template).find(".title-container a.author").html(recommendation["author_name"]);
                    $(template).find(".title-container a.author").data("id", recommendation["author_id"]);

                    let averageReview = recommendation["average_rating"];
                    $(template).find(".rating-container .average-review").html(averageReview);
                    changeElemStars($(template).find(".rating-container .rating i"), averageReview);
                    $(template).find(".rating-container .num-review").html(recommendation["number_ratings"]);

                    $(template).find(".synopsis").html(recommendation["synopsis"])

                    $(template).find(".book-info .date-added").html(recommendation["date_added"]);
                    $(template).find(".book-info .match-strength").html(recommendation["certainty"]);

                    let genres = recommendation["genres"];
                    for (let k = 0; k < Object.keys(genres).length; k++) {
                        let genreTemplate = $(template).find(".book-genres ol li.template").clone().removeClass("template");
                        $(genreTemplate).find("a").html(genres[k]);
                        $(genreTemplate).appendTo($(template).find(".book-genres ol"));
                    }

                    $(template).find(".actions button.read").data("id", result["list_id"]);

                    $(template).appendTo(".recommendation-entries");
                }

                assignAuthorNavigationHandlers();
                assignGenreNavigationHandlers();
                assignBookNavigationHandlers();
                assignDeleteRecommendationHandlers();
                assignMoveRecommendationHandlers();
            } else {
                $(".initial-preference").removeClass("hidden");
                $(".recommendation-entries").addClass("hidden");
                let itemPerCol = Math.floor((iterateLength / 3));
                for (let col = 0; col < 3; col++) {
                    for (let row = 0; row < itemPerCol; row++) {
                        let author = result["data"][(col * itemPerCol) + row];
                        addNewAuthorSelectionBox(author["name"], author["id"], col);
                    }
                }

                if (!itemPerCol % 3) {
                    let author = result["data"][result["data"].length - 1];
                    addNewAuthorSelectionBox(author["name"], author["id"], 0);
                }

                assignPreferenceSubmissionHandlers();
            }
        },
        error: function (jqXHR) {
            if (jqXHR.status == 403) {
                sessionExpired();
            }
            console.log(jqXHR.status + " " + jqXHR.responseText);
        }
    });
}

function addNewAuthorSelectionBox (authorName, authorID, columnNum) {
    // https://www.techiedelight.com/dynamically-create-checkbox-with-javascript/
    $(".initial-preference form.preferences .column").eq(columnNum).append(
        $(document.createElement("input")).prop({
            id: authorID,
            name: authorName,
            value: authorID,
            type: "checkbox"
        })
    ).append(
        $(document.createElement("label")).prop({
            for: authorID
        }).html(authorName)
    ).append(document.createElement('br'));
}

function assignPreferenceSubmissionHandlers () {
    $(".initial-preference form.preferences").off("submit");
    $(".initial-preference form.preferences").on("submit", function (event) {
        event.preventDefault();
        // https://stackoverflow.com/a/590040/21124864 (comment by Duvrai)
        $.ajax({
            type: "POST",
            url: "/cgi-bin/recommendations/set_user_preferences",
            data: JSON.stringify({
                "authors": $("input[type=checkbox]:checked").map(function() {return $(this).attr("value")}).get(),
                "session_id": sessionID
            }),
            success: function () {reloadCurrentPage()},
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
                console.log(jqXHR.status + " " + jqXHR.responseText);
            },
            async: false  // Means that it waits for recommendations to be generated before reloading
        });
    });
}

function assignDeleteRecommendationHandlers () {
    $(".book .actions button.delete").off("click");
    $(".book .actions button.delete").click(function () {
        let book = $(this).closest(".book");
        $.ajax({
            type: "POST",
            url: "/cgi-bin/recommendations/remove_recommendation",
            data: JSON.stringify({
                "book_id": $(book).data("id"),
                "session_id": sessionID
            }),
            success: function (result) {
                $(book).fadeOut(500); // Hide the entry from the list
            },
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
                console.log(jqXHR.status + " " + jqXHR.responseText);
            }
        });
    });
}

function assignMoveRecommendationHandlers () {
    $(".book .actions button.read").off("click");
    $(".book .actions button.read").click(function () {
        let book = $(this).closest(".book");
        $.ajax({
            type: "POST",
            url: "/cgi-bin/recommendations/add_list_entry",
            data: JSON.stringify({
                "book_id": $(book).data("id"),
                "session_id": sessionID,
                "list_id": $(this).data("id")
            }),
            success: function (result) {
                $(book).fadeOut(500); // Hide the entry from the list
            },
            error: function (jqXHR) {
                if (jqXHR.status == 403) {
                    sessionExpired();
                }
                console.log(jqXHR.status + " " + jqXHR.responseText);
            }
        });
    });
}

// -----------------------------------------------------------------------------
// Search feature
// -----------------------------------------------------------------------------
$("header nav.bottom .search form").on("submit", function (event) {
    event.preventDefault();
    let query = $(this).find("input[type='search']").val();
    switchPageContent(null, "search", async=false); // Cannot be async, as it could arrive after the next query
    changeActiveLink(null, "Browse"); // Change page to browse page
    if (query != "") {
        $.ajax({
            type: "GET",
            url: addGetParameter("/cgi-bin/search/search", "query", query),
            success: function (result) {
                let length = Object.keys(result).length;
                if (length > 0) {
                    $(".search-container .alert").addClass("hidden");
                    for (let i = 0; i < length; i++) {
                        let currentRes = result[i];
                        let type = currentRes["type"];
                        let template;
                        if (type == "a") {
                            template = $(".search-container .row.author-search.template").clone().removeClass("template");
                            $(template).find("a.author").html(currentRes["name"]);
                            $(template).find("a.author").data("id", currentRes["author_id"]);
                        } else if (type == "b") {
                            template = $(".search-container .row.book.template").clone().removeClass("template");
                            $(template).data("id", currentRes["book_id"]);
                            $(template).find("a.author-name").html(currentRes["author"]);
                            $(template).find("a.book-button").html(currentRes["title"]);
                            $(template).find(".cover img").attr("src", currentRes["cover"]);
                        } else {
                            template = $(".search-container .row.genre-search.template").clone().removeClass("template");
                            $(template).find("a.genre-button").html(currentRes["name"]);
                        }
                        $(template).find("p.match-strength span").html(currentRes["certainty"]);

                        $(template).appendTo(".search-container");
                    }
                    assignBookNavigationHandlers();
                    assignAuthorNavigationHandlers();
                    assignGenreNavigationHandlers();
                } else {
                    $(".search-container .alert").removeClass("hidden");
                }
            },
            error: function (jqXHR) {
                console.log(jqXHR.status + " " + jqXHR.responseText);
            }
        });
    } else {
        $(".search-container .alert").removeClass("hidden");
    }
})

// -----------------------------------------------------------------------------
// Browse Page
// -----------------------------------------------------------------------------
function loadBrowsePage () {
    $.ajax({
        type: "GET",
        url: addGetParameter("/cgi-bin/search/get_browse_data", "session_id", sessionID), // Using search does not make sense as the
        // page is called browse, but semantically, and search is used for the search feature, so is logical
        success: function (result) {
            addHomePageDetails(result["trending"], "trending");
            addHomePageDetails(result["newest_additions"], "newest");
            addHomePageDetails(result["highly_rated"], "highly-rated");  // These will always have a value.

            $(".row#because-added .added-name").html(result["because_added_title"]);
            let becauseAdded = result["because_added"];
            if (becauseAdded == null) { // Will only be null if there is no user, so all user specifics can
                // be hidden.
                $(".row#because-added").addClass("hidden"); // Remove so the hr disappears. These will reappear on sign in
            } else if (becauseAdded.length == 0) {
                $(".row#because-added").addClass("hidden");
            } else {
                $(".row#because-added").removeClass("hidden");
                addHomePageDetails(becauseAdded, "because-added");
            }

            $(".row#because-read .read-name").html(result["because_read_title"]);
            let becauseRead = result["because_read"];
            if (becauseRead == null) { // Will only be null if there is no user, so all user specifics can
                // be hidden.
                $(".row#because-read").addClass("hidden"); // Remove so the hr disappears. These will reappear on sign in
            } else if (becauseRead.length == 0) {
                $(".row#because-read").addClass("hidden");
            } else {
                $(".row#because-read").removeClass("hidden");
                addHomePageDetails(becauseRead, "because-read");
            }

            let favouriteAuthors = result["favourite_authors"];
            if (favouriteAuthors == null) { // Will only be null if there is no user, so all user specifics can
                // be hidden.
                $(".row#author-following").addClass("hidden"); // Remove so the hr disappears. These will reappear on sign in
            } else if (favouriteAuthors.length == 0) {
                $(".row#author-following").addClass("hidden");
            } else {
                $(".row#author-following").removeClass("hidden");
                addHomePageDetails(favouriteAuthors, "author-following");
            }

            changeNumVisibleSummaries(); // Needs to run once, as resize will not trigger by this point
            assignBookNavigationHandlers();
        },
        error: function (jqXHR) {
            if (jqXHR.status == 403) {
                sessionExpired();
            }
        }
    })
}

// -----------------------------------------------------------------------------
// window onload handlers
// -----------------------------------------------------------------------------
$(document).ready(function () {
    let cookie = $.cookie.get("sessionID");
    if (cookie) {
        sessionID = cookie;
        changeAccountButtons();
    }
    reloadCurrentPage();
})
