function play(name){
fetch("/videoPlay",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({name})
})

setInterval(()=>{
fetch("/videoFrame")
},50)
}
