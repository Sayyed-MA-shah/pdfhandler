import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from PyPDF2 import PdfReader, PdfWriter
import os
import uuid
import threading


# Define function to upload PDFs
def upload_pdfs():
    global pdf_files
    pdf_files = filedialog.askopenfilenames()
    pdf_count = len(pdf_files)
    pdf_label.config(text=str(pdf_count) + " PDFs selected")


# Define function to update metadata
def update_metadata():
    # Get metadata information from text fields
    title = title_entry.get()
    author = author_entry.get()
    subject = subject_entry.get()
    output_directory = directory_entry.get()

    # Get current date and time
    now = datetime.datetime.utcnow()

    # Extract keywords from user input
    user_keywords = keywords_entry.get()
    user_keywords = [keyword.strip().lower() for keyword in user_keywords.split(',')] if user_keywords else []

    # Process each PDF file
    def process_pdfs():
        num_pdfs = len(pdf_files)
        processed_pdfs = 0

        for pdf_filename in pdf_files:
            with open(pdf_filename, 'rb') as f:
                pdf_reader = PdfReader(f)

                # Extract title from PDF
                if '/Title' in pdf_reader.metadata:
                    title = pdf_reader.metadata['/Title']
                    title_entry.delete(0, tk.END)
                    title_entry.insert(0, title)
                else:
                    tk.messagebox.showwarning("Warning", "PDF title not found.")

                # Extract keywords from PDF text content
                pdf_text = ""
                for page_num in range(len(pdf_reader.pages)):
                    pdf_text += pdf_reader.pages[page_num].extract_text()

                nltk.download('punkt')
                nltk.download('stopwords')
                stop_words = set(stopwords.words('english'))
                tokens = nltk.word_tokenize(pdf_text)
                lemmatizer = WordNetLemmatizer()
                keywords = [lemmatizer.lemmatize(word.lower()) for word in tokens if word.lower() not in stop_words]

                # Remove duplicates and limit the number of keywords to 20
                keywords = list(set(keywords))[:20]

                # Append user-specified keywords
                keywords.extend(user_keywords)

                # Join the keywords into a comma-separated string
                keywords = ", ".join(keywords)

                # Create PDF writer object
                pdf_writer = PdfWriter()

                # Copy pages from reader to writer
                for page_num in range(len(pdf_reader.pages)):
                    pdf_writer.add_page(pdf_reader.pages[page_num])

                # Add metadata to writer
                pdf_writer.add_metadata({
                    '/Title': title,
                    '/Author': author,
                    '/Subject': subject,
                    '/Keywords': keywords,
                    '/CreationDate': now.strftime('%Y%m%d%H%M%S'),
                    '/ModDate': now.strftime('%Y%m%d%H%M%S'),
                    '/Producer': 'GPL Ghostscript 10.01.1: modified using pdfrw',
                    '/Creator': 'PP2 幸福'
                })

                # Generate random output filename
                if not os.path.exists(output_directory):
                    os.makedirs(output_directory)

                random_name = str(uuid.uuid4()) + "_optim.pdf"
                output_filename = os.path.join(output_directory, random_name)

                # Save the updated PDF to the output file
                with open(output_filename, 'wb') as output_file:
                    pdf_writer.write(output_file)

                processed_pdfs += 1

                if processed_pdfs == num_pdfs:
                    messagebox.showinfo("Success", "All PDFs have been processed.")
        
        # Clear text fields and update UI
        title_entry.delete(0, tk.END)
        author_entry.delete(0, tk.END)
        subject_entry.delete(0, tk.END)
        keywords_entry.delete(0, tk.END)
        pdf_label.config(text="")
        directory_entry.delete(0, tk.END)

    # Create a new thread for processing PDFs
    pdf_thread = threading.Thread(target=process_pdfs)
    pdf_thread.start()



# Create the main window
window = tk.Tk()
window.title("PDF Metadata Updater")
window.geometry("500x300")
window.configure(bg="#36344D")

# Create title label
title_label = tk.Label(window, text="Title:", bg="#36344D", fg="white", font=("Arial", 10, "bold"))
title_label.grid(row=0, column=0, sticky=tk.W)

# Create title entry
title_entry = tk.Entry(window, width=50)
title_entry.grid(row=0, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)

# Create author label
author_label = tk.Label(window, text="Author:", bg="#36344D", fg="white", font=("Arial", 10, "bold"))
author_label.grid(row=1, column=0, sticky=tk.W)

# Create author entry
author_entry = tk.Entry(window, width=50)
author_entry.grid(row=1, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)

# Create subject label
subject_label = tk.Label(window, text="Subject:", bg="#36344D", fg="white", font=("Arial", 10, "bold"))
subject_label.grid(row=2, column=0, sticky=tk.W)

# Create subject entry
subject_entry = tk.Entry(window, width=50)
subject_entry.grid(row=2, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)

# Create keywords label
keywords_label = tk.Label(window, text="Keywords:", bg="#36344D", fg="white", font=("Arial", 10, "bold"))
keywords_label.grid(row=3, column=0, sticky=tk.W)

# Create keywords entry
keywords_entry = tk.Entry(window, width=50)
keywords_entry.grid(row=3, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)

# Create PDF upload button
upload_button = ttk.Button(window, text="Upload PDFs", command=upload_pdfs)
upload_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)

# Create PDF label
pdf_label = tk.Label(window, text="", bg="#36344D", fg="white", font=("Arial", 10, "bold"))
pdf_label.grid(row=4, column=2, columnspan=2, sticky=tk.W)

# Create save directory label
directory_label = tk.Label(window, text="Save Directory:", bg="#36344D", fg="white", font=("Arial", 10, "bold"))
directory_label.grid(row=5, column=0, sticky=tk.W)

# Create save directory entry
directory_entry = tk.Entry(window, width=50)
directory_entry.grid(row=5, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)

# Create update metadata button
update_button = ttk.Button(window, text="Update Metadata", command=update_metadata)
update_button.grid(row=6, column=0, columnspan=4, padx=10, pady=10)

# Run the main window
window.mainloop()
