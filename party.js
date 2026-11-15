// Elegant birthday decorations: a few slow gold sparkles in the background, and a soft gold confetti fall
// when the final podium or a "答對" screen appears. Purely visual; it never touches the game state.
(()=>{
  const COLORS=["#f0dcae","#d6b46e","#fbf7f0","#e7b9b0","#c9a35a"];
  const reduce=matchMedia("(prefers-reduced-motion:reduce)").matches;
  function sparkles(){
    const box=document.createElement("div");box.className="pg-sparkles";box.setAttribute("aria-hidden","true");
    const n=innerWidth<700?10:22;
    for(let i=0;i<n;i++){const s=document.createElement("i");
      s.style.left=Math.random()*100+"%";s.style.top=Math.random()*100+"%";
      s.style.setProperty("--s",(2+Math.random()*3).toFixed(1)+"px");
      s.style.setProperty("--dur",(5+Math.random()*5).toFixed(1)+"s");s.style.setProperty("--del",(-Math.random()*8).toFixed(1)+"s");
      box.appendChild(s)}
    document.body.prepend(box);
  }
  let last=0;
  function confetti(n){
    if(reduce||Date.now()-last<2500)return;last=Date.now();
    const box=document.createElement("div");box.className="pg-confetti";box.setAttribute("aria-hidden","true");
    for(let i=0;i<n;i++){const c=document.createElement("i");
      c.style.left=Math.random()*100+"%";c.style.background=COLORS[i%COLORS.length];
      if(i%4===0){c.style.width=c.style.height="7px";c.style.borderRadius="50%"}
      c.style.setProperty("--dx",(Math.random()*120-60)+"px");c.style.setProperty("--rot",(240+Math.random()*600)+"deg");
      c.style.setProperty("--dur",(3+Math.random()*2.5)+"s");c.style.setProperty("--del",(Math.random()*.8)+"s");
      box.appendChild(c)}
    document.body.appendChild(box);setTimeout(()=>box.remove(),7000);
  }
  window.partyConfetti=confetti;
  function watch(){
    const seen=new WeakSet();
    new MutationObserver(()=>{
      const p=document.querySelector(".podium,.status.good");
      if(p&&!seen.has(p)){seen.add(p);confetti(p.classList.contains("podium")?110:40)}
    }).observe(document.body,{childList:true,subtree:true});
  }
  const go=()=>{sparkles();watch()};
  document.readyState==="loading"?document.addEventListener("DOMContentLoaded",go):go();
})();
