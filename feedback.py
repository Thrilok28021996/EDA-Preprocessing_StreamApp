"""This module provides a feedback form function for Streamlit applications."""

import streamlit as st


def feedback(info):
    """
    Create and display a feedback form using Streamlit and HTML.

    Args:
        info (dict): A dictionary containing user information. Must include an 'Email' key.

    Returns:
        None. The function displays the form using Streamlit's st.markdown().
    """
    st.subheader("📨 Contact Me")
    email = info["Email"]
    contact_form = f"""
    <style>
        input[type=text], input[type=email], textarea {{
            width: 100%;
            padding: 12px 20px;
            margin: 8px 0;
            display: inline-block;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }}
        button[type=submit] {{
            width: 100%;
            background-color: #4CAF50;
            color: white;
            padding: 14px 20px;
            margin: 8px 0;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }}
        button[type=submit]:hover {{
            background-color: #45a049;
        }}
        .form-container {{
            background-color: #f2f2f2;
            padding: 20px;
            border-radius: 5px;
        }}
    </style>
    <form id="contactForm" action="https://formsubmit.co/{email}" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="text" name="name" placeholder="Your name" required>
        <input type="email" name="email" placeholder="Your email" required>
        <textarea name="message" placeholder="Your feedback here" required></textarea>
        <button type="submit">Send</button>
    </form>
    <script>
        document.getElementById('contactForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            fetch(this.action, {{
                method: 'POST',
                body: new FormData(this)
            }}).then(response => {{
                if (response.ok) {{
                    this.reset();
                    alert('Message sent successfully!');
                }} else {{
                    alert('There was an error sending your message. Please try again.');
                }}
            }});
        }});
    </script>
    """
    st.markdown(contact_form, unsafe_allow_html=True)
