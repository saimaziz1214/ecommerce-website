
  
   
   
   const searchButton = document.querySelector('a[href="search.html"]');
      const searchContainer = document.getElementById("searchContainer");
      const searchInput = document.getElementById("searchInput");

      searchButton.addEventListener("click", function (e) {
        e.preventDefault();
        searchContainer.style.display = "block";
        searchInput.focus();
      });

      // javascript for pagination
      const dots = document.querySelectorAll(".dot");
      const productCards = document.querySelectorAll(
        ".products-grid .product-card"
      );

      const itemsPerPage = 4;

      function showPage(page) {
        const start = (page - 1) * itemsPerPage;
        const end = page * itemsPerPage;

        productCards.forEach((card, index) => {
          if (index >= start && index < end) {
            card.style.display = "flex";
          } else {
            card.style.display = "none";
          }
        });

        dots.forEach((dot) => dot.classList.remove("active"));
        document
          .querySelector(`.dot[data-page="${page}"]`)
          .classList.add("active");
      }

      // Initialize first page
      showPage(1);

      // Dot click events
      dots.forEach((dot) => {
        dot.addEventListener("click", () => {
          const page = parseInt(dot.getAttribute("data-page"));
          showPage(page);
        });
      });

      
      
      
      
      
      
      
      // Subscription form handling
 