from flask import Flask, request, redirect, send_file, render_template
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}
app.config['OUTPUT_FOLDER'] = 'outputs'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['OUTPUT_FOLDER']):
    os.makedirs(app.config['OUTPUT_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the file
        df = pd.read_csv(file_path)
        column_name = df.columns[1]
        duplicates = df[column_name].duplicated(keep=False)

        def highlight_duplicates(val, is_duplicate):
            if is_duplicate:
                return 'background-color: red'
            return ''

        styled_df = df.style.apply(
            lambda x: ['background-color: red' if v else '' for v in duplicates],
            subset=[column_name]
        )

        output_filename = f"output_{filename.rsplit('.', 1)[0]}.xlsx"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        styled_df.to_excel(output_path, engine='openpyxl', index=False)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

if __name__ == '__main__':
    app.run(debug=True)