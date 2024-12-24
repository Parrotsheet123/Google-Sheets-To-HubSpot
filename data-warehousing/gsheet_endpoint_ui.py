import tkinter as tk
import requests
import json
from tkinter import ttk, Frame, messagebox, Scrollbar

class GsheetUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Google Sheets to JSON API Request Sender")
        self.window.configure(bg="black")
        self.window.minsize(800, 600)
        self.create_tabs()

    def create_tabs(self):
        container = Frame(self.window, bg="black")
        container.pack(fill="both", expand=True)

        self.tabs = ttk.Notebook(container)
        self.tabs.pack(fill="both", expand=True)

        self.tab1 = Frame(self.tabs, bg="#1f2925")
        self.tab2 = Frame(self.tabs, bg="#1f2925")
        self.tabs.add(self.tab1, text="GSheet To HubSpot")
        self.tabs.add(self.tab2, text="Extract Data")

        self.create_widgets(self.tab1, self.create_test_request_widgets)
        self.create_widgets(self.tab2, self.create_extract_data_widgets)

    def create_widgets(self, tab, widget_creator):
        main_canvas = tk.Canvas(tab, bg="#1f2925")
        scrollbar = Scrollbar(tab, orient="vertical", command=main_canvas.yview)
        scrollable_frame = Frame(main_canvas, bg="#1f2925")

        scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        widget_creator(scrollable_frame)

    def create_test_request_widgets(self, frame):
        self.api_entry_label = self.create_label_entry(frame, "API Endpoint (URL):", 40)
        self.additional_headers_text = self.create_text_input(frame, "Additional Headers (JSON format):", 5, '{"Authorization": "Bearer YOUR_TOKEN"}\n')
        self.request_body_text = self.create_text_input(frame, "Request Body (JSON format):", 10)
        self.test_request_button = self.create_button(frame, "Test Request", self.test_request)  # Uses test_request
        self.create_response_sect = self.create_response_section(frame)

    def create_extract_data_widgets(self, frame):
        tk.Label(frame, text="Extract Data from Google Sheets", bg="#1f2925", fg="white").pack(anchor="center", padx=5, pady=5)
        self.create_button(frame, "Extract Data", self.test_request)
        self.extracted_data_output = self.create_text_input(frame, "", 20)

    def create_label_entry(self, frame, label_text, entry_width):
        tk.Label(frame, text=label_text, bg="#1f2925", fg="white").pack(anchor="w", padx=5, pady=5)
        entry = tk.Entry(frame, width=entry_width, bg="black", fg="green", insertbackground="white")
        entry.pack(fill="x", padx=5, pady=5)
        setattr(self, label_text.split()[0].lower() + "_entry", entry)

    def create_text_input(self, frame, label_text, height, default_text=""):
        tk.Label(frame, text=label_text, bg="#1f2925", fg="white").pack(anchor="w", padx=5, pady=5)
        text_box = tk.Text(frame, wrap=tk.WORD, height=height, bg="black", fg="green", insertbackground="white")
        text_box.pack(fill="both", padx=5, pady=5, expand=True)
        text_box.insert("1.0", default_text)
        return text_box

    def create_button(self, frame, button_text, command):
        button = tk.Button(frame, text=button_text, command=command)
        button.pack(fill="x", pady=10)

    def create_response_section(self, frame):
        tk.Label(frame, text="Response:", bg="#1f2925", fg="white").pack(anchor="w", padx=5, pady=5)
        self.response_output = self.create_text_input(frame, "", 10)

    def test_request(self):
      # Retrieve the user inputs from the respective fields
      endpoint = self.api_entry.get()  # Get the URL from the entry widget
      headers_text = self.additional_headers_text.get("1.0", "end-1c").strip()  # Get headers from text box
      body_text = self.request_body_text.get("1.0", "end-1c").strip()  # Get body from text box

      # Check if URL is provided
      if not endpoint:
          messagebox.showerror("Error", "API Endpoint (URL) is required.")
          return

      # Try to parse the headers and body as JSON
      try:
          headers = json.loads(headers_text) if headers_text else {}
          body = json.loads(body_text) if body_text else {}
      except json.JSONDecodeError:
          messagebox.showerror("Error", "Invalid JSON format in headers or body.")
          return

      # Correct the request body format: wrap the "inputs" in a list
      try:
          # Wrap the "inputs" in a list
          request_body = {
              "inputs": [body]  # Note the list around "body"
          }

          print(f"Request body: {json.dumps(request_body, indent=4)}")

          response = requests.post(
              url=endpoint,
              headers=headers,
              json=request_body
          )

          # Debugging: print the response content
          print(f"Response status code: {response.status_code}")
          print(f"Response content: {response.text}")

          response.raise_for_status()  # Check if the request was successful

          # If the request was successful, update the response text box with the response
          self.update_text_output(self.response_output, response.json())

      except requests.RequestException as e:
          messagebox.showerror("Error", f"Request failed: {str(e)}")
      except Exception as e:
          messagebox.showerror("Error", f"Failed to send request: {str(e)}")


    def update_text_output(self, text_widget, data):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, json.dumps(data, indent=4))
        text_widget.config(state=tk.DISABLED)

    def run(self):
        self.window.mainloop()

# Run the application
if __name__ == "__main__":
    app = GsheetUI()
    app.run()
