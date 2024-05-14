if(document.readyState == 'loading'){
    document.addEventListener('DOMContentLoaded', ready)
} else{
    ready()
}

function ready(){
    var removeButton = document.getElementsByClassName('btn-danger')
    for(var i = 0; i < removeButton.length; i++) {
        var button = removeButton[i]
        button.addEventListener('click', removeItem) 
        } 
    }
    
    function removeItem(event) {
        var buttonClicked = event.target
        buttonClicked.parentElement.parentElement.remove()
        updateCart()
    }
    
    function updateCart(){
        var itemContainer = document.getElementsByClassName('cart-items')[0]
        var cartRows = itemContainer.getElementsByClassName('cart-row')
        var total = 0
        for(var i = 0; i < cartRows.length; i++) {
            var cartRow = cartRows[i]
            var priceElement = cartRow.getElementsByClassName('cart-price')[0]
            var quantityElement = cartRow.getElementsByClassName('cart-quantity-input')
            [0]
            var price = parseFloat(priceElement.innerText.replace('$', ''))
            var quantity = quantityElement.value
            total = total + (price * quantity)
        }
        total = Math.round(total * 100) / 100
        document.getElementsByClassName('cart-total-price')[0].innerText = '$' + total
    }
    
        var quantityInput = document.getElementsByClassName('cart-quantity-input')
        for( var i = 0; i < quantityInput.length; i++) {
            var input = quantityInput[i]
            input.addEventListener('change', quantityChanged)
        }
    
    function quantityChanged(event){
        var input = event.target
        if (isNaN(input.value) || input.value <= 0) {
            input.value = 1
        }
        updateCart()
    }
    
        var addButton = document.getElementsByClassName('shop-item-button')
        for( var i = 0; i < addButton.length; i++){
            var button = addButton[i]
            button.addEventListener('click', addToCartClicked)
        }
    
    function addToCartClicked(event){
        var button = event.target
        var shopItem = button.parentElement.parentElement
        var title = shopItem.getElementsByClassName('title')[0].innerText
        var price = shopItem.getElementsByClassName('shop-item-price')[0].innerText
        addItemToCart(title, price)
        updateCart()
    }
    
    function addItemToCart(title, price) {
        var cartRow = document.createElement('div')
        cartRow.classList.add('cart-row')
        var cartItems = document.getElementsByClassName('cart-items')[0]
        var cartItemNames = cartItems.getElementsByClassName('title')
        for (var i = 0; i < cartItemNames.length; i++) {
            if (cartItemNames[i].innerText == title) {
                alert('Already added to cart')
                return
            }
        }
        var cartRowContents = `
            <div class="cart-item cart-column">
                <span class="title" id='title'>${title}</span>
            </div>
            <span class="cart-price cart-column" id='cart-price'>${price}</span>
            <div class="cart-quantity cart-column">
                <input class="cart-quantity-input" type="number" value="1">
                <button class="btn btn-danger" type="button">REMOVE</button>
            </div> `
        cartRow.innerHTML = cartRowContents
        cartItems.append(cartRow)
        cartRow.getElementsByClassName('btn-danger')[0].addEventListener('click', removeItem)
        cartRow.getElementsByClassName('cart-quantity-input')[0].addEventListener('change', quantityChanged)
    
        // Send an AJAX request to insert the item into the cart table
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/add_to_cart', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function () {
            if (xhr.status === 200) {
                console.log('Item added to cart:', xhr.responseText);
                updateCart();
            } else {
                console.error('Failed to add item to cart:', xhr.responseText);
            }
        };
        xhr.send(JSON.stringify({ title: title, price: price }));
    }
    
    
    function purchaseClicked(){

        let reciept = document.getElementById('title').innerText
        let price = document.getElementById('cart-price').innerText
        let orderName = document.getElementById('nameInput').value
        localStorage.setItem(reciept, price,)
        location.replace('receipt.html')
  
    


        var cartItems = document.getElementsByClassName('cart-items')[0]
        while (cartItems.hasChildNodes()){
            cartItems.removeChild(cartItems.firstChild)
        }
        updateCart()
    }
