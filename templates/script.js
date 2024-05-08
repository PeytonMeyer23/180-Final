function showProductDetails(product) {
    var productDetailsBox = document.getElementById("product-details-box");
    var productDetails = document.getElementById("product-details");

    productDetails.innerHTML = '';

    var productImage = document.createElement("img");
    productImage.src = product.imageURL;
    productImage.className = "product-image";
    productDetails.appendChild(productImage);

    var productName = document.createElement("div");
    productName.innerHTML = "<strong>Product Name:</strong> " + product.title;
    productDetails.appendChild(productName);

    var productPrice = document.createElement("div");
    productPrice.innerHTML = "<strong>Price:</strong> " + product.price;
    productDetails.appendChild(productPrice);

    var productDescription = document.createElement("div");
    productDescription.innerHTML = "<strong>Description:</strong> " + product.description;
    productDetails.appendChild(productDescription);

    var addToCartBtn = document.createElement("button");
    addToCartBtn.className = "add-to-cart-btn";
    addToCartBtn.innerHTML = "Add to Cart";
    productDetails.appendChild(addToCartBtn);

    addToCartBtn.addEventListener('click', function() {   // literally an empty function cuz i havent made cart yet
        // Add cart functionality here
        console.log("Product added to cart: " + product.productID);
    });

    // Show product details box
    productDetailsBox.style.display = "block";
}

function hideProductDetails() {
    var productDetailsBox = document.getElementById("product-details-box");
    productDetailsBox.style.display = "none";
}