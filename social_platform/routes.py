from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from .database import db

from .models import (
    User,
    Post,
    Comment,
    Rating,
    DetectionResult
)


social_bp = Blueprint(
    "social",
    __name__
)


# =========================================================
# HOME
# =========================================================

@social_bp.route("/")
def index():

    if current_user.is_authenticated:
        return redirect(
            url_for("social.home")
        )

    return redirect(
        url_for("social.login")
    )


# =========================================================
# REGISTER
# =========================================================

@social_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            flash(
                "Username and password are required.",
                "error"
            )

            return redirect(
                url_for("social.register")
            )

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            flash(
                "Username already exists.",
                "error"
            )

            return redirect(
                url_for("social.register")
            )

        user = User(
            username=username,
            password=generate_password_hash(
                password
            )
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Account created successfully.",
            "success"
        )

        return redirect(
            url_for("social.login")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@social_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(
                url_for("social.home")
            )

        flash(
            "Invalid username or password.",
            "error"
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@social_bp.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("social.login")
    )


# =========================================================
# HOME FEED
# =========================================================

@social_bp.route("/home")
@login_required
def home():

    posts = Post.query.order_by(
        Post.created_at.desc()
    ).all()

    return render_template(
        "home.html",
        posts=posts
    )


# =========================================================
# CREATE POST
# =========================================================

@social_bp.route(
    "/post",
    methods=["POST"]
)
@login_required
def create_post():

    content = request.form.get(
        "content",
        ""
    ).strip()

    if content:

        post = Post(
            user_id=current_user.id,
            content=content
        )

        db.session.add(post)
        db.session.commit()

    return redirect(
        url_for("social.home")
    )


# =========================================================
# COMMENT
# =========================================================

@social_bp.route(
    "/comment/<int:post_id>",
    methods=["POST"]
)
@login_required
def create_comment(post_id):

    text = request.form.get(
        "text",
        ""
    ).strip()

    if text:

        comment = Comment(
            post_id=post_id,
            user_id=current_user.id,
            text=text
        )

        db.session.add(comment)
        db.session.commit()

    return redirect(
        url_for("social.home")
    )


# =========================================================
# RATING
# =========================================================

@social_bp.route(
    "/rate",
    methods=["POST"]
)
@login_required
def create_rating():

    item_id = request.form.get(
        "item_id",
        ""
    ).strip()

    rating_value = request.form.get(
        "rating",
        "0"
    )

    try:

        rating_value = int(
            rating_value
        )

    except ValueError:

        rating_value = 0

    if (
        item_id
        and 1 <= rating_value <= 5
    ):

        rating = Rating(
            user_id=current_user.id,
            item_id=item_id,
            rating=rating_value
        )

        db.session.add(rating)
        db.session.commit()

    return redirect(
        url_for("social.home")
    )


# =========================================================
# PROFILE
# =========================================================

@social_bp.route("/profile")
@login_required
def profile():

    posts = Post.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Post.created_at.desc()
    ).all()

    results = DetectionResult.query.filter_by(
        user_id=current_user.id
    ).order_by(
        DetectionResult.created_at.desc()
    ).limit(20).all()

    return render_template(
        "profile.html",
        user=current_user,
        posts=posts,
        results=results
    )