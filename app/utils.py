from zipfile import ZipFile

from app.models import Issue


def save_metadata_to_cbz(path: str, issue: Issue):
    genres = ",".join(list(issue.comic.genres.values_list("name", flat=True)))
    web = issue.remote_id if issue.source == "readallcomics" else ""
    issue_number = (
        int(issue.issue) if int(issue.issue) == issue.issue else issue.issue
    )  # remove .0 suffix
    xml_content = f"""
<ComicInfo>
    <Title>{issue.comic.name}</Title>
    <Series>{issue.comic.name}</Series>
    <Number>{issue_number}</Number>
    <Volume>{issue.volume}</Volume>
    <Year>{issue.year}</Year>
    <Publisher>{issue.comic.publisher}</Publisher>
    <Genre>{genres}</Genre>
    <Web>{web}</Web>
</ComicInfo>
    """

    with ZipFile(path, "a") as z:
        z.writestr("ComicInfo.xml", xml_content)
