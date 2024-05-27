from flask import Flask, render_template, request, redirect, url_for, session, flash
import db

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route('/')
def index():
    categories = db.get_categories()
    categories_with_counts = []
    for category in categories:
        post_count = db.number_posts_cat([category['category_id']])
        categories_with_counts.append({
            'category_id': category['category_id'],
            'category': category['category'],
            'post_count': post_count
        })

    total_activity = None
    if 'user_id' in session:
        total_activity = db.total_activity([session['user_id']])
    return render_template('home.html', categories=categories_with_counts, total_activity=total_activity)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        try:
            db.call_proc([email, username, password])
            flash('User registered successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.login([username, password])
        if user:
            session['user_id'] = user[0]['user_id']
            session['username'] = user[0]['username']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/category/<int:category_id>')
def view_category(category_id):
    threads = db.threads([category_id])
    if threads is None:
        threads = []
    return render_template('category.html', threads=threads)

@app.route('/thread/<int:post_id>', methods=['GET', 'POST'])
def view_thread(post_id):
    if request.method == 'POST' and 'user_id' in session:
        comment = request.form['comment']
        db.add_comment([session['user_id'], comment, post_id])
    comments = db.get_comments_post([post_id])
    if comments is None:
        comments = []

    post = db.get_post([post_id])[0]
    like_count = db.count_likes_for_thread(post_id)
    return render_template('thread.html', post=post, comments=comments, like_count=like_count)

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' in session:
        user_id = session['user_id']
        existing_like = db.get_like([user_id, post_id])
        if not existing_like:
            db.insert_like([post_id, user_id])
        else:
            flash('You have already liked this post.', 'warning')
    return redirect(url_for('view_thread', post_id=post_id))

@app.route('/category/<int:category_id>/new_post', methods=['GET', 'POST'])
def new_post(category_id):
    if 'user_id' not in session:
        flash('You need to be logged in to create a post', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        user_id = session['user_id']
        db.add_post([title, body, category_id, user_id])
        flash('Post created successfully!', 'success')
        return redirect(url_for('view_category', category_id=category_id))
    
    return render_template('new_post.html', category_id=category_id)

@app.route('/update_info', methods=['GET', 'POST'])
def update_info():
    if 'user_id' not in session:
        flash('You need to be logged in to update your information', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_email = request.form.get('email')
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        current_username = session['username']

        if new_email:
            db.email_change([new_email, current_username])
            flash('Email updated successfully!', 'success')

        if new_username:
            db.name_change([new_username, current_username])
            session['username'] = new_username  # Update the session with new username
            flash('Username updated successfully!', 'success')

        if new_password:
            db.pass_change([new_password, current_username])
            flash('Password updated successfully!', 'success')

        return redirect(url_for('update_info'))

    return render_template('update_info.html')

@app.route('/delete_post/<int:post_id>', methods=['GET'])
def delete_post(post_id):
    if 'user_id' in session:
        post = db.Select("SELECT user_id FROM posts WHERE post_id = %s", [post_id])
        if post and post[0]['user_id'] == session['user_id']:
            db.delete_post([post_id])
            flash('Post deleted successfully.', 'success')
        else:
            flash('You do not have permission to delete this post.', 'danger')
    else:
        flash('You need to be logged in to delete a post.', 'warning')
    return redirect(request.referrer)

@app.route('/delete_comment/<int:comment_id>', methods=['GET'])
def delete_comment(comment_id):
    if 'user_id' in session:
        comment = db.Select("SELECT user_id FROM comments WHERE comment_id = %s", [comment_id])
        if comment and comment[0]['user_id'] == session['user_id']:
            db.delete_comment([comment_id])
            flash('Comment deleted successfully.', 'success')
        else:
            flash('You do not have permission to delete this comment.', 'danger')
    else:
        flash('You need to be logged in to delete a comment.', 'warning')
    return redirect(request.referrer)

@app.route('/unlike_post/<int:post_id>', methods=['POST'])
def unlike_post(post_id):
    if 'user_id' in session:
        user_id = session['user_id']
        success = db.delete_like([user_id, post_id])  # Pass both user_id and post_id
        if success == 0:
            flash('Like removed successfully.', 'success')
        else:
            flash('Failed to remove like.', 'danger')
    return redirect(request.referrer)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
