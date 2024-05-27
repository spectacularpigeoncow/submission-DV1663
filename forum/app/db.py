import mysql.connector

def connect_DB():
        db = mysql.connector.connect(
                host = "db",
                user = "root",
                password = "root",
                database = "project"
                )
        
        return db


def Select(query, params=None):
    db = connect_DB()

    if db:
        cursor = db.cursor(dictionary=True)

        try:
            if params:
                cursor.execute(query,params)

            else:
                cursor.execute(query)

            result = cursor.fetchall()
            return result

        except Exception as e:
            print(f"Error Select func: {e}")
            db.rollback()

        finally:
            cursor.close()
            db.close()


# args in order = email, username, password
def call_proc(args):
    db = connect_DB()

    if db:
        cursor = db.cursor(dictionary=True)
        
        try:
            cursor.callproc('add_user',args)
            db.commit()

            for result in cursor.stored_results():
                row = result.fetchall()
            return row[0]['ret_val']
        except Exception as e:
            print(f"Error in procedure exec: {e}")
            db.rollback()

        finally:
            cursor.close()
            db.close()


def insert(query,args):
    db = connect_DB()

    if db:
        cursor = db.cursor()

        try:
            cursor.execute(query,args)
            db.commit()
            return 0

        except Exception as e:
            print(f"Error in insert query: {e}")
            return 1

        finally:
            cursor.close()
            db.close()



def delete(query,args):
    db = connect_DB()

    if db:
        cursor = db.cursor()
        
        try:
            cursor.execute(query,args)
            db.commit()

            if(cursor.rowcount > 0):
                return 0
            else:
                return 1
        except Exception as e:
            print(f"Error in delete query: {e}")
            return 1
        finally:
            cursor.close()
            db.close()

def add_comment(args):
    query = "insert into comments(user_id,comment,post_id,posted_at) values (%s,%s,%s,current_date())"
    sucess = insert(query,args)
    return sucess

def add_post(args):
    query = "INSERT INTO posts(title, post, category_id, user_id, created_at) VALUES(%s, %s, %s, %s, CURRENT_TIMESTAMP)"
    success = insert(query, args)
    return success

def delete_post(args):
    del_comments_query = "delete from comments where post_id = %s"
    delete(del_comments_query,args)
    del_likes_query = "delete from likes where post_id = %s"
    delete(del_likes_query,args)
    query = "delete from posts where post_id = %s"
    sucess = delete(query,args)
    return sucess

def delete_comment(args):
    query = "delete from comments where comment_id = %s"
    sucess = delete(query,args)
    return sucess

def email_change(args):
    query = "update users set email = %s where username = %s"
    sucess = insert(query,args)
    return sucess

def get_like(args):
    query = "SELECT * FROM likes WHERE user_id = %s AND post_id = %s"
    result = Select(query, args)
    return result

def delete_like(args):
    query = "delete from likes where user_id = %s and post_id = %s"
    sucess = delete(query,args)
    return sucess

def insert_like(args):
    query = "insert into likes(post_id, user_id) values(%s,%s)"
    sucess = insert(query,args)
    return sucess

def login(args): # Kan användas för att spara user info också
    query = "SELECT user_id, username FROM users WHERE username = %s AND password = SHA2(%s, 256)"
    result = Select(query, args)
    return result

def name_change(args):
    query = "update users set username = %s where username = %s"
    sucess = insert(query,args)
    return sucess

def pass_change(args):
    query = "update users set password = sha2(%s,256) where username = %s"
    sucess = insert(query,args)
    return sucess

def get_user_posts(args):
    query = "select category, post_id, posts.category_id, username, title, post, posts.created_at from posts left join users on posts.user_id = users.user_id left join categories on posts.category_id = categories.category_id where posts.user_id = %s"
    result = Select(query,args)
    return result

def get_comments_post(args):
    query = "SELECT username, comment, comment_id, comments.user_id, posted_at FROM comments LEFT JOIN users ON comments.user_id = users.user_id WHERE post_id = %s order by posted_at desc"
    result = Select(query, args)
    if result is None:
        result = []
    return result

def get_post(args):
    query = "select created_at, category_id,post_id,username, post,title from posts left join users on posts.user_id = users.user_id where posts.post_id = %s"
    result = Select(query,args)
    return result

def posted_at(args): 
    query = "select username, comment, comment_id, posted_at from comments left join users on comment.user_id = users.user_id where post_id = %s order by posted_at desc limit 1"
    result = Select(query,args)
    return result

#Adds the total number of posts and comments made by a user. Args = user_id
def total_activity(args):
    query = "SELECT total_activity(%s) AS activity"
    result = Select(query, args)
    return result[0]['activity'] if result else 0

def get_categories():
    query = "select category, category_id from categories"
    result = Select(query)
    return result

def number_posts_cat(args):
    query = "SELECT COUNT(*) AS post_count FROM posts WHERE category_id = %s"
    result = Select(query, args)
    return result[0]['post_count'] if result else 0

def latest_post_cat(args):
    query = "select category_id, created_at from posts where category_id = %s order by created_at desc limit 1"
    result = Select(query,args)
    return result

def threads(args):
    query = "SELECT category, username, posts.user_id, created_at, title, post, posts.category_id, posts.post_id FROM posts LEFT JOIN categories ON posts.category_id = categories.category_id LEFT JOIN users ON posts.user_id = users.user_id WHERE posts.category_id = %s ORDER BY posts.created_at DESC"
    result = Select(query, args)
    if result is None:
        result = []
    return result

def count_likes_for_thread(post_id):
    query = "SELECT COUNT(*) AS like_count FROM likes WHERE post_id = %s"
    result = Select(query, [post_id])
    if result:
        return result[0]['like_count']
    else:
        return 0
