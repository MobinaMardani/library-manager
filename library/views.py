from datetime import date

from django.http import Http404
from django.shortcuts import redirect, render

from .sample_data import books, members, borrowings


def find_book(book_id):
    return next((b for b in books if b["id"] == book_id), None)


def find_member(member_id):
    return next((m for m in members if m["id"] == member_id), None)


def home(request):
    return render(request, "library/home.html")


def book_list(request):
    query = request.GET.get("q", "").strip().lower()
    filtered_books = books
    if query:
        filtered_books = [
            book for book in books
            if query in book["title"].lower()
            or query in book["author"].lower()
        ]
    return render(request, "library/book_list.html", {
        "books": filtered_books,
        "members": members,
        "query": query,
    })


def member_list(request):
    return render(request, "library/member_list.html", {"members": members})


def borrow_book(request, book_id, member_id):
    book = find_book(book_id)
    member = find_member(member_id)
    if request.method == "POST" and book and member and book["available"]:
        book["available"] = False
        book["borrow_count"] += 1
        borrowings.append({
            "book_id": book_id,
            "member_id": member_id,
            "borrowed_at": date.today().isoformat(),
            "returned_at": None,
        })
    return redirect("book_list")


def return_book(request, book_id):
    book = find_book(book_id)
    if request.method == "POST" and book and not book["available"]:
        book["available"] = True
        for item in reversed(borrowings):
            if item["book_id"] == book_id and item["returned_at"] is None:
                item["returned_at"] = date.today().isoformat()
                break
    return redirect("book_list")


def member_history(request, member_id):
    member = find_member(member_id)
    if member is None:
        raise Http404("Member not found")
    history = [
        {**item, "book": find_book(item["book_id"])}
        for item in borrowings
        if item["member_id"] == member_id
    ]
    return render(request, "library/history.html", {
        "member": member,
        "history": history,
    })


def statistics(request):
    available_books = [b for b in books if b["available"]]
    borrowed_books = [b for b in books if not b["available"]]
    most_popular = max(books, key=lambda b: b["borrow_count"], default=None)
    return render(request, "library/statistics.html", {
        "total_books": len(books),
        "available_books": len(available_books),
        "borrowed_books": len(borrowed_books),
        "total_members": len(members),
        "most_popular": most_popular,
    })


def borrowing_overview(request):
    def enrich(item):
        return {
            **item,
            "book": find_book(item["book_id"]),
            "member": find_member(item["member_id"]),
        }

    current = [enrich(i) for i in borrowings if i["returned_at"] is None]
    returned = [enrich(i) for i in borrowings if i["returned_at"] is not None]
    return render(request, "library/borrowings.html", {
        "current": current,
        "returned": returned,
    })
