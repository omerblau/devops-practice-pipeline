fetch("http://backend:5000/api/quote")
    .then((res) => res.json())
    .then((data) => {
        document.getElementById("quote").innerText = data.quote;
    })
    .catch((err) => {
        document.getElementById("quote").innerText = "Error fetching quote.";
    });
