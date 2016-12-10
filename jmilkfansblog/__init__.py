from flask import Flask, redirect, url_for
from flask.ext.login import current_user
from flask.ext.principal import identity_loaded, UserNeed, RoleNeed

from jmilkfansblog.models import db
from jmilkfansblog.controllers import blog, main
from jmilkfansblog.controllers.restful.posts import PostApi
from jmilkfansblog.controllers.restful.auth import AuthApi
from jmilkfansblog.extensions import bcrypt, openid, login_manager, principals
from jmilkfansblog.extensions import restful_api


def create_app(object_name):
    """Create the app instance via `Factory Method`"""

    app = Flask(__name__)
    # Set the config for app instance
    app.config.from_object(object_name)
    
    # Will be load the SQLALCHEMY_DATABASE_URL from config.py to db object
    db.init_app(app)
    # Init the Flask-Bcrypt via app object
    bcrypt.init_app(app)
    # Init the Flask-OpenID via app object
    openid.init_app(app)
    # Init the Flask-Login via app object
    login_manager.init_app(app)
    # Init the Flask-Prinicpal via app object
    principals.init_app(app)

    # Define the route of restful_api
    restful_api.add_resource(
        PostApi,
        '/api/posts',
        '/api/posts/<string:post_id>',
        endpoint='restful_api_post')

    restful_api.add_resource(
        AuthApi,
        '/api/auth',
        endpoint='restful_api_auth')

    # Init the Flask-Restful via ap object
    restful_api.init_app(app)


    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        """Change the role via add the Need object into Role.

           Need the access the app object.
        """

        # Set the identity user object
        identity.user = current_user

        # Add the UserNeed to the identity user object
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        # Add each role to the identity user object
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))
    
    # Register the Blueprint into app object
    app.register_blueprint(blog.blog_blueprint)
    app.register_blueprint(main.main_blueprint)

    return app
