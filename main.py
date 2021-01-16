import random
from pathlib import Path
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn import metrics
from joblib import dump, load
from jobsearch.dataaccess import JobPost, JobPostLabel, get_session
from jobsearch import jobs
from jobsearch import remoteok


app = typer.Typer()
console = Console()
model_path = Path("./instance/model.joblib")


def transform_jp(jp: remoteok.RemoteOkJobPost) -> JobPost:
    return JobPost(
        id=jp.id,
        url=jp.url,
        company=jp.company,
        position=jp.position,
        description=jp.description,
        location=jp.location,
        tags=",".join(jp.tags)
    )


@app.command()
def fetch_new():
    console.print("[yellow]Fetching jobs...[/yellow]!")
    job_list = remoteok.fetch_jobs()
    job_list = [transform_jp(job_post) for job_post in job_list]
    with get_session() as session:
        last_job = jobs.get_last(session)
        if last_job is not None:
             job_list = [job_post for job_post in job_list if job_post.id > last_job.id]
        jobs.save(session, job_list)
    console.print("[green]Done![/green]")


@app.command()
def label():
    while True:
        with get_session() as session:
            jp = jobs.get_next_for_labelling(session)
            if not jp:
                console.print("[red]No job posts available for labelling[/red]")
                break
            console.clear()
            console.print(f"[yellow]{jp.position}[/yellow]\n")
            console.print(f"[blue]{jp.company}[/blue]\n")
            console.print(f"[brown]{jp.tags}[/brown]\n")
            console.print(f"Location: {jp.location}\n")
            console.print(Markdown(f"{jp.description}"))
            result = typer.prompt("\n\nIs the job post relevant? [y yes/n no/q quit]", "n")
            if result in ["n", "no"]:
                jp.label = JobPostLabel.NOT_INTERESTED
                jobs.update(session, jp)
            if result in ["y", "yes"]:
                jp.label = JobPostLabel.INTERESTED
                jobs.update(session, jp)
            if result in ["q", "quit"]:
                console.clear()
                break


@app.command()
def train():
    console.clear()
    console.print("[yellow]Training...[/yellow]!")
    job_clf = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', SGDClassifier()),
    ])
    with get_session() as session:
        labeled = jobs.get_labeled(session)
        if len(labeled) == 0:
            console.print("[red]No job posts available for labelling[/red]")
            return
    x = [jp.text for jp in labeled]
    y = [jp.label for jp in labeled]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size = 0.2, random_state = random.randint(1, 1000)
    )
    job_clf.fit(x_train, y_train)
    predicted = job_clf.predict(x_test)
    print(metrics.classification_report(
        y_test, predicted, target_names=["not interested", "interested"], labels=[0, 1])
    )
    dump(job_clf, model_path)


@app.command()
def recommend():
    if not model_path.is_file():
        console.print("[red]Model is not trained yet[/red]")
        return
    with get_session() as session:
        job_list = jobs.get_not_labeled(session)
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Position", style="dim")
    table.add_column("Url")
    job_clf = load(model_path)
    predicted = job_clf.predict([jp.text for jp in job_list])
    console.print("[yellow]Recommended jobs:[/yellow]")
    for i, jp in enumerate(job_list):
        if predicted[i] == JobPostLabel.INTERESTED:
            table.add_row(jp.position, jp.url)    
    console.print(table)


if __name__ == "__main__":
    app()