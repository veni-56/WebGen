from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@shopwave.com').first():
        db.session.add(User(
            name='Admin',
            email='admin@shopwave.com',
            password=generate_password_hash('admin123'),
            role='admin'
        ))
        db.session.commit()
        print('Admin seeded: admin@shopwave.com / admin123')

if __name__ == '__main__':
    app.run(debug=True)
