from gitmostwanted.models.repo import Repo, RepoStars
from gitmostwanted.app import db, celery
from sqlalchemy.sql import expression
from statistics import variance, mean


@celery.task()
def repos_status_hopeless():
    repos = Repo.query.filter().filter(Repo.status == 'unknown')
    for repo in repos:
        result = db.session.query(RepoStars.day, RepoStars.stars)\
            .filter(RepoStars.repo_id == repo.id)\
            .order_by(expression.asc(RepoStars.day))\
            .all()
        if not result:
            continue

        chunks = result_split(list(result_normalize(result, 28)), 7)
        for chunk in chunks:
            print(variance(chunk))
            if variance(chunk) >= 1000:
                continue

            if mean(chunk) < 1:
                print("{} is hopeless".format(repo.id))
                continue

            print("{} is promising".format(repo.id))


def result_normalize(lst: list, num_days: int):
    fst = lst[0][0]
    lst = dict(lst)
    for i in range(num_days):
        key = fst + i
        yield 0 if key not in lst else lst[key]


def result_split(lst: list, num_rows: int):
    num_segments = len(lst) // num_rows
    for i in range(num_segments):
        yield lst[(i*num_rows):((i+1)*num_rows)]
