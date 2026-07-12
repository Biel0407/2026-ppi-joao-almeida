from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from treino.auth import login_required
from treino.db import get_db

bp = Blueprint("exercise", __name__)


@bp.route("/")
def index():
    db = get_db()
    exercises = db.execute(
        """
        SELECT e.id,
               e.name,
               e.muscle_group,
               e.sets,
               e.reps,
               e.weight,
               e.created,
               e.author_id,
               u.username
        FROM exercise e
        JOIN user u ON e.author_id = u.id
        ORDER BY e.created DESC
        """
    ).fetchall()

    return render_template("exercise/index.html", exercises=exercises)


@bp.route("/exercise/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        name = request.form["name"]
        muscle_group = request.form["muscle_group"]
        sets = request.form["sets"]
        reps = request.form["reps"]
        weight = request.form["weight"]

        error = None

        if not name:
            error = "O nome do exercício é obrigatório."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                """
                INSERT INTO exercise
                (name, muscle_group, sets, reps, weight, author_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    muscle_group,
                    sets,
                    reps,
                    weight,
                    g.user["id"],
                ),
            )
            db.commit()
            return redirect(url_for("exercise.index"))

    return render_template("exercise/create.html")


def get_exercise(id, check_author=True):
    exercise = get_db().execute(
        """
        SELECT e.id,
               e.name,
               e.muscle_group,
               e.sets,
               e.reps,
               e.weight,
               e.created,
               e.author_id,
               u.username
        FROM exercise e
        JOIN user u ON e.author_id = u.id
        WHERE e.id = ?
        """,
        (id,),
    ).fetchone()

    if exercise is None:
        abort(404, "Exercício não encontrado.")

    if check_author and exercise["author_id"] != g.user["id"]:
        abort(403)

    return exercise


@bp.route("/exercise/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    exercise = get_exercise(id)

    if request.method == "POST":
        name = request.form["name"]
        muscle_group = request.form["muscle_group"]
        sets = request.form["sets"]
        reps = request.form["reps"]
        weight = request.form["weight"]

        error = None

        if not name:
            error = "O nome do exercício é obrigatório."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                """
                UPDATE exercise
                SET name = ?,
                    muscle_group = ?,
                    sets = ?,
                    reps = ?,
                    weight = ?
                WHERE id = ?
                """,
                (
                    name,
                    muscle_group,
                    sets,
                    reps,
                    weight,
                    id,
                ),
            )
            db.commit()
            return redirect(url_for("exercise.index"))

    return render_template("exercise/update.html", exercise=exercise)


@bp.route("/exercise/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_exercise(id)

    db = get_db()
    db.execute("DELETE FROM exercise WHERE id = ?", (id,))
    db.commit()

    return redirect(url_for("exercise.index"))