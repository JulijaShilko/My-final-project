# # app.py
# from flask import Flask, render_template
# from flask_wtf import FlaskForm
# from wtforms import StringField, FormField, FieldList, IntegerField, Form
# from wtforms.validators import Optional
# from collections import namedtuple

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'keepthissecret'

# class ProductForm(Form):
#     title = StringField('Title')
#     price = IntegerField('Price', validators=[Optional()])

# class InventoryForm(FlaskForm):
#     category_name = StringField('Category Name')
#     products = FieldList(FormField(ProductForm), min_entries=4, max_entries=8)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     form = InventoryForm()
#     return render_template('index.html', form=form)


# <!-- templates/index.html -->
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>FieldList Example</title>
# </head>
# <body>
#     <form method="POST" action="">
#         {{ form.hidden_tag() }}
#         {{ form.category_name.label }} {{ form.category_name }}
#         <br />
#         {% for nested in form.products %}
#             {{ nested.label }}{{ nested }}
#         {% endfor %}
#         <button>Submit</button>
#     </form>
# </body>
# </html>



    <!-- <div class="row">
      {% for program in current_user.programs %}
        <div class="col-md-6 mb-4">
          <div class="card h-100">
            <div class="card-body">
              <h5 class="card-title">{{ program.discription }}</h5>
              <p class="card-text">Created on {{ program.date.strftime('%B %d, %Y') }}</p>
              <a href="{{ url_for('program', program_id=program.id) }}" class="btn btn-primary">View program</a>
            </div>
          </div>
        </div>
      {% endfor %}
    </div> -->