const text = document.querySelector(".span1");

const load = () => {
     setTimeout(() =>{
      text.textContent = "Dark Say's!";
    },0);
    setTimeout(() =>{
        text.textContent = "Don't Forget key!";
      },5000);
  
}

setInterval(load, 5000);


function cho(){
  document.getElementById("file").click();
}

document.getElementById("file").addEventListener("change",() =>{
  document.getElementById("loading").style.display = "flex";
  document.getElementById("sta").innerText = "Please wait...";
  document.getElementById("sta").style.color = "#03bcf4";
  document.getElementById("upload").submit();
})

function rem(){
  document.getElementById("sta").innerText = "Please wait...";
  document.getElementById("sta").style.color = "#03bcf4";
  document.getElementById("remove").submit();
}
