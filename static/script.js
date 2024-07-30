const text = document.querySelector(".span1");
const load = () => {
             setTimeout(() =>{
              text.textContent = "Dark Say!";
            },0);
            setTimeout(() =>{
                text.textContent = "Don't Forget key!";
              },5000);
          
        }

        setInterval(load, 5000);
