from flask import Flask, render_template, request
from PIL import Image
import os
from io import BytesIO  
import base64

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('preview.html')

@app.route('/convert', methods=['POST', 'GET'])
def convert():
    if request.method == 'POST':
        files = request.files.getlist('images')  # match HTML input name
        convert_type = request.form.get('convert_type')

        if not files or not convert_type:
            return "No file or conversion type selected", 400
        
        if convert_type == 'images_to_pdf':
            images = []
            
            for file in files:
                if file.filename == '':
                    continue  # Skip empty files

                img = Image.open(file.stream).convert('RGB')  # Use stream to avoid file handle issues
                images.append(img)

            if not images:
                return "No valid images found", 400

            pdf_io = BytesIO()
            images[0].save(pdf_io, 'PDF', save_all=True, append_images=images[1:])
            pdf_io.seek(0)
            data = pdf_io.getvalue()  # Read once to avoid pointer issues

            output_name = f"converted.pdf"
            data_hex = data.hex()

            preview_data = None
            mime_type = 'application/pdf'

            previews = [{
                'download_name': output_name,
                'file_data': data_hex,
                'preview': preview_data,
                'mime_type': mime_type
            }]

            return render_template('convert.html', previews=previews)

        previews = []
        for file in files:
            if file.filename == '':
                continue  # Skip empty files

            img = Image.open(file.stream)  # Use stream to avoid file handle issues
            base_name = os.path.splitext(file.filename)[0]

            img_io = BytesIO()

            if convert_type == 'jpg_to_png':
                output_ext = 'png'
                img.save(img_io, 'PNG')
            elif convert_type == 'png_to_jpg':
                output_ext = 'jpg'
                img = img.convert('RGB')
                img.save(img_io, 'JPEG')
            else:
                return "Invalid conversion type", 400
            
            output_name = f"{base_name}.{output_ext}"
            img_io.seek(0)
            data = img_io.getvalue()  # Read once to avoid pointer issues
            
            data_hex = data.hex()
            
            if output_ext == 'pdf':
                preview_data = None
                mime_type = 'application/pdf'
            else:
                img_base64 = base64.b64encode(data).decode('utf-8')
                preview_data = f"data:image/{output_ext};base64,{img_base64}"
                mime_type = f'image/{output_ext}'
                
            previews.append({
                'download_name': output_name,
                'file_data': data_hex,
                'preview': preview_data,
                'mime_type': mime_type
            })
            
        return render_template('convert.html', previews=previews)

    else:
        # GET: Render empty form
        return render_template('convert.html', previews=None)

@app.template_filter('hex_to_base64')
def hex_to_base64_filter(s):
    return base64.b64encode(bytes.fromhex(s)).decode('utf-8')

@app.route('/size', methods=['POST', 'GET'])
def size():
    if request.method == 'GET':
        return render_template('size.html', previews=None)
    files = request.files.getlist('images')
    width = request.form.get('width')
    height = request.form.get('height')
    
    if not files or not width or not height:
        return "No file or dimensions provided", 400
    
    for file in files:
        continue  # Skip empty files

        img = Image.open(file.stream)
        resized_img = img.resize((width, height))

        img_io = BytesIO()
        resized_img.save(img_io, format='PNG')
        img_io.seek(0)
        data = img_io.getvalue()
        data_hex = data.hex()

        preview_data = f"data:image/png;base64,{base64.b64encode(data).decode('utf-8')}"
        mime_type = 'image/png'

        previews.append({
            'download_name': f"resized_{file.filename}",
            'file_data': data_hex,
            'preview': preview_data,
            'mime_type': mime_type
        })

    return render_template('size.html', previews=previews)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
>>>>>>> 5e4ecc4 (Initial commit)
