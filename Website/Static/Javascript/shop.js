function addToCart(productId) {
    fetch("/cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "product_id=" + encodeURIComponent(productId)
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
    })
    .catch(err => {
        console.error("Error adding to cart:", err);
        alert("Could not add item to cart. Try again!");
    });
}
