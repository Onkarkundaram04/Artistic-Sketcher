import os
import cv2
import numpy as np
import base64
from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

main_bp = Blueprint("main_bp", __name__)

# Allowed extensions for image upload
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def pencil_sketch_effect(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
    sobel = cv2.magnitude(sobelx, sobely)
    sobel = np.uint8(np.clip(sobel, 0, 255))
    _, edge_mask = cv2.threshold(sobel, 50, 255, cv2.THRESH_BINARY)

    gamma = 0.5
    gamma_corrected = np.array(255 * (gray / 255) ** gamma, dtype="uint8")

    inverted_edge = cv2.bitwise_not(edge_mask)
    sketch = cv2.addWeighted(gamma_corrected, 0.8, inverted_edge, 0.2, 0)

    return sketch


def colored_sketch_effect(image, style="pencil"):
    if style == "pencil":
        color_smoothed = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edges_inv = cv2.bitwise_not(edges)
        edges_inv_color = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
        output = cv2.multiply(color_smoothed, edges_inv_color, scale=1 / 255)
        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        return output
    elif style == "cartoon":
        color_smoothed = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_blurred = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(
            gray_blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2
        )
        edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        output = cv2.bitwise_and(color_smoothed, edges_color)
        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        return output
    elif style == "impressionist":
        warm = image.copy()
        warm[:, :, 2] = cv2.add(warm[:, :, 2], 10)
        warm[:, :, 1] = cv2.add(warm[:, :, 1], 10)
        warm_smoothed = cv2.bilateralFilter(warm, d=9, sigmaColor=75, sigmaSpace=75)
        gray = cv2.cvtColor(warm, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edges_inv = cv2.bitwise_not(edges)
        edges_inv_color = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
        output = cv2.addWeighted(warm_smoothed, 0.8, edges_inv_color, 0.2, 0)
        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        return output
    else:
        return image


def image_to_base64(img, is_gray=False):
    if is_gray:
        success, buffer = cv2.imencode(".png", img)
    else:
        success, buffer = cv2.imencode(".png", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if not success:
        return None
    return base64.b64encode(buffer).decode("utf-8")


@main_bp.route("/", methods=["GET", "POST"])
def index():
    processed_image = None
    all_sketches = None
    style_choice = "1"
    if request.method == "POST":
        style_choice = request.form.get("style", "1")

        # Handling image upload if present
        if "image" in request.files and request.files["image"].filename != "":
            file = request.files["image"]
            if not allowed_file(file.filename):
                return redirect(request.url)
            filename = secure_filename(file.filename)
            file_bytes = np.frombuffer(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if img is None:
                return redirect(request.url)
            # Store image in session
            success, buffer = cv2.imencode(".png", img)
            if success:
                session["image_data"] = base64.b64encode(buffer).decode("utf-8")
        # Use stored image if no new uploads
        elif "image_data" in session:
            img_data = base64.b64decode(session["image_data"])
            img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                return redirect(request.url)
        else:
            return redirect(request.url)

        # Processing the image based on style choice
        if style_choice == "1":
            result = colored_sketch_effect(img, style="pencil")
            is_gray = False
            processed_image = image_to_base64(result, is_gray=is_gray)
        elif style_choice == "2":
            result = colored_sketch_effect(img, style="cartoon")
            is_gray = False
            processed_image = image_to_base64(result, is_gray=is_gray)
        elif style_choice == "3":
            result = colored_sketch_effect(img, style="impressionist")
            is_gray = False
            processed_image = image_to_base64(result, is_gray=is_gray)
        elif style_choice == "4":
            result = pencil_sketch_effect(img)
            is_gray = True
            processed_image = image_to_base64(result, is_gray=is_gray)
        elif style_choice == "5":
            all_sketches = {
                "pencil": image_to_base64(
                    colored_sketch_effect(img, style="pencil"), is_gray=False
                ),
                "cartoon": image_to_base64(
                    colored_sketch_effect(img, style="cartoon"), is_gray=False
                ),
                "impressionist": image_to_base64(
                    colored_sketch_effect(img, style="impressionist"), is_gray=False
                ),
                "pencil_sketch": image_to_base64(
                    pencil_sketch_effect(img), is_gray=True
                ),
            }
        else:
            result = colored_sketch_effect(img, style="pencil")
            is_gray = False
            processed_image = image_to_base64(result, is_gray=is_gray)

    return render_template(
        "index.html",
        processed_image=processed_image,
        all_sketches=all_sketches,
        selected_style=style_choice,
    )
