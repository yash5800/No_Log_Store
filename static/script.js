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
  if(confirm("Are you sure you want to Remove?")){
      console.log("Removing");
    document.getElementById("sta").innerText = "Please wait...";
       document.getElementById("sta").style.color = "#03bcf4";
   return true;
  }
  else{
    console.log('no delete');
    return false;
  }
}
