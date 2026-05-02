from app import create_app, db
from app.models import User, SellerProfile

app = create_app()

@app.cli.command('init-db')
def init_db():
    """Create/migrate tables and seed admin user."""
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@meesho.com').first():
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@meesho.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print('Admin created: admin@meesho.com / admin123')
        else:
            print('DB already initialised.')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
