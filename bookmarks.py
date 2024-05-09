from dataclasses import dataclass
import subprocess
import sys


@dataclass
class Bookmark:
    title: str
    start: int
    end: int | None


def get_section_numbers(pdf_path: str) -> list[Bookmark]:
    p = subprocess.Popen(["pdftk", pdf_path, "dump_data"], stdout=subprocess.PIPE)
    bookmarks = []
    if p.stdout:
        lines = p.stdout.readlines()
        current_start = None
        current_level = None
        current_title = None
        for i in range(0, len(lines)):
            line = lines[i]
            decoded = line.decode("utf-8").strip()
            splits = decoded.split(": ")
            if splits[0] == "BookmarkTitle":
                number = splits[1].split(" ")[0]
                level = int(lines[i + 1].decode("utf-8").strip().split(": ")[1])
                # The current chapter is over
                if current_level is None or level <= current_level:
                    page = int(lines[i + 2].decode("utf-8").strip().split(": ")[1])
                    # If we are in a chapter, end it and add the bookmark to the list
                    if current_title is not None and current_start is not None:
                        previous_bookmark = Bookmark(
                            current_title, current_start, page - 1
                        )
                        bookmarks.append(previous_bookmark)
                        current_start = None
                        current_title = None
                        current_level = None
                    # A new chapter is starting
                    if number.isnumeric() and "." not in number:
                        current_title = splits[1]
                        current_start = page
                        current_level = level
                    else:
                        current_title = None
        if current_start is not None and current_title is not None:
            last_bookmark = Bookmark(current_title, current_start, None)
            bookmarks.append(last_bookmark)
    return bookmarks


def perform_split(pdf_path: str, start: int, end: int | None, output: str):
    if end is None:
        end_string = "end"
    else:
        end_string = str(end)
    subprocess.run(
        ["pdftk", pdf_path, "cat", f"{start}-{end_string}", "output", f"{output}.pdf"]
    )


def get_chapter_title(root: str, bookmark: Bookmark):
    words = bookmark.title.split(" ")
    number = f"{int(words[0]):02d}"
    title = "-".join(words[1:]).lower()
    return f"{root}-chapter-{number}-{title}"


def split_pdf(pdf_path: str, bookmarks: list[Bookmark], root: str):
    for bookmark in bookmarks:
        perform_split(
            pdf_path,
            bookmark.start,
            bookmark.end,
            get_chapter_title(root, bookmark),
        )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <pdf file> <output root>")
        exit(1)
    else:
        pdf_path = sys.argv[1]
        bookmarks = get_section_numbers(pdf_path)
        root = sys.argv[2]
        split_pdf(pdf_path, bookmarks, root)
