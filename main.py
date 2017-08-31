from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.sql import func 
from app import app, db
from models import Blog, User
from hashutils import check_pw_hash


def user_validation(username):

    username_error = ""

    if username == "":
        username_error = "Please enter a valid username"
    else:
        if len(username) < 4:
            username_error = "Username must be greater than 3 characters"
        if len(username) > 20:
            username_error = "Username must be less than 20 characters"
    for i in username:
        if i.lower() not in "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()/<>{}[]|+=-_~`\"\'\\.,?;:":
            username_error = "Username cannot contain spaces"

    return username_error

    

def password_validation(password):
    
    password_error = ""

    if password == "":
        password_error = "Please enter a valid password"
    else:
        if len(password) < 4:
            password_error = "Password must be greater than 3 characters"
        if len(password) > 20:
            password_error = "Password must be less than 20 characters"
    for i in password:
        if i.lower() not in "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()/<>{}[]|+=-_~`\"\'\\.,?;:":
            password_error = "Password cannot contain spaces"

    return password_error


def verify_validation(verify):
    password = request.form["password"]
    verify_error = ""
    if verify != password:
        verify_error = "Passwords do not match"

    return verify_error

@app.before_request
def require_login():
    blocked_routes = ["new_post"]
    if request.endpoint in blocked_routes and "username" not in session:
        return redirect("/login")

@app.route("/")
def index():
    total_users = User.query.all()
    return render_template("index.html", total_users=total_users)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        username_check = request.form["username"]
        password_check = request.form["password"]
        verify_check = request.form["verify"]

        if user_validation(username_check) != "" or password_validation(password_check) != "" or verify_validation(verify_check) != "":
            return render_template("signup.html", username_error=flash(user_validation(username_check)), password_error=flash(password_validation(password_check)), verify_error=flash(verify_validation(verify_check)), username=username_check)
        else:
            existing_user = User.query.filter_by(username=username_check).first()
            if not existing_user:
                new_user = User(username_check, password_check)
                db.session.add(new_user)
                db.session.commit()
                session["username"] = username_check
                return redirect("/blog/newpost")
            else:
                redirect("/signup", flash("User already exists"))
        
    return render_template("signup.html")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/blog")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_check = request.form["username"]
        password_check = request.form["password"]
        user = User.query.filter_by(username=username_check).first()
        while user_validation(username_check) != "" or password_validation(password_check) != "":
            return render_template("login.html", username_error=flash(user_validation(username_check)), password_error=flash(password_validation(password_check)), username=username_check)
        if user and check_pw_hash(password_check, user.pw_hash):
            session["username"] = username_check
            return redirect("/blog/newpost")
        else:
            redirect("/login", flash("Invalid Login Information"))
        
        
    return render_template("login.html")



@app.route("/blog", methods=["GET", "POST"])
def blog_page():
    
    user = User.query.all()
    all_blogs = Blog.query.order_by(desc(Blog.pub_date)).all()
    total_blogs = Blog.query.all()
    user_id = request.args.get("user")
    blog_id = request.args.get("id")
    
    owner = User.query.filter_by(username=user_id).first()
    final_blogs = Blog.query.filter_by(owner=owner).order_by(desc(Blog.pub_date)).all()



    if blog_id != None:
        new_id = int(blog_id) - 1
        
        return render_template("blog_post.html", blog=total_blogs[new_id], user=user)
        

    for name in user:
        if name.username == user_id:
            
            return render_template("singleUser.html", user=name.username, final_blogs=final_blogs)

    return render_template("blog.html", user=user, all_blogs=all_blogs)
    

@app.route("/blog/newpost", methods=["POST", "GET"])
def new_post():
    white_space = []
    space = " "
    for i in range(1000):
        white_space.append(space)
        space += " "
    owner = User.query.filter_by(username=session["username"]).first()
    if request.method == "POST":
        body_error = ""
        title_error = ""
        post_title = request.form["post-title"]
        post_body = request.form["post-body"]
        if post_title == "" or post_title in white_space:
            title_error = "Please fill in the title"
        if post_body == "" or post_body in white_space:
            body_error = "Please fill in the body"
        elif post_title and post_body != "":
            
            blog = Blog(post_title, post_body, owner)
            db.session.add(blog)
            db.session.commit()
            return redirect("/blog?id={}".format(blog.id))
        return render_template("newpost.html", title="Add Blog Entry", title_error=title_error, body_error=body_error, post_body=post_body, post_title=post_title)
    else:
        return render_template("newpost.html",title="Add Blog Entry")



if __name__ == "__main__":
    app.run()