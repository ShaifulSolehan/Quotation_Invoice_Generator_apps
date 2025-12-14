from flask import Flask, render_template, request, make_response
from weasyprint import HTML
from io import BytesIO
from num2words import num2words
from datetime import datetime
import os

app = Flask(__name__)

def get_next_invoice_number():
    counter_file = 'invoice_counter.txt'

    # Make sure the file exists
    if not os.path.exists(counter_file):
        with open(counter_file, 'w') as f:
            f.write("1000")

    # Read current number
    with open(counter_file, 'r') as f:
        current = int(f.read().strip())

    # Increment and save
    next_number = current + 1
    with open(counter_file, 'w') as f:
        f.write(str(next_number))

    return f"RME{current}"  # Return current, then increase for next

@app.route('/')
def index():
    return render_template('invoice_form.html')

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    doc_type = request.form['doc_type']
    #Get invoice number
    invoice_number = get_next_invoice_number() if doc_type == "INVOICE" else None
    # Get the raw price from the form
    raw_price = request.form['price']
    # Convert to words
    price_words = num2words(raw_price, lang='en').upper()
    price_words = f"RINGGIT MALAYSIA {price_words} ONLY"
    #Change the date format
    event_date_raw = request.form['event_date']
    event_date = datetime.strptime(event_date_raw, '%Y-%m-%d').strftime('%d-%m-%Y')
    # Collect form data
    invoice = {
        "doc_type": doc_type,
        "invoice_no": invoice_number,  # You can make this dynamic later
        "date": request.form['date'],
        "customer_name": request.form['customer_name'],
        "customer_address": request.form['customer_address'],
        #"description": request.form['description'],
        "price": request.form['price'],
        "price_words":price_words,
        "song": request.form.get('song') or None,
        "event": request.form['event'],
        "event_venue": request.form['event_venue'],
        "event_date": event_date,
    }

    # Render template
    rendered = render_template("invoice_print.html", invoice=invoice)

    # Convert to PDF
    pdf = HTML(string=rendered, base_url=request.root_url).write_pdf()

    # Set filename
    if doc_type == "INVOICE":
        filename = f"INVOICE_{invoice_number}.pdf"
    else:
        filename = "QUOTATION.pdf"
    # Send as download
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

if __name__ == '__main__':
    app.run(debug=True)
