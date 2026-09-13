import React,{useState} from "react";
import {api} from "../lib/api";
export default function Auth({onAuth}){
 const [register,setRegister]=useState(false),[name,setName]=useState(""),[email,setEmail]=useState(""),[password,setPassword]=useState(""),[error,setError]=useState("");
 async function submit(e){e.preventDefault();setError("");try{const d=await api(register?"/api/auth/register":"/api/auth/login",{method:"POST",body:JSON.stringify(register?{name,email,password}:{email,password})});localStorage.setItem("apf_token",d.token);onAuth(d.user)}catch(x){setError(x.message)}}
 return <main className="authPage"><div className="authCard"><div className="brand">APF <span>GAMES</span></div><p className="muted">Автомобильные игры. XP. Рейтинг.</p><form onSubmit={submit}>{register&&<input placeholder="Имя" value={name} onChange={e=>setName(e.target.value)} required/>}<input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required/><input type="password" placeholder="Пароль" value={password} onChange={e=>setPassword(e.target.value)} required/><button className="primary full">{register?"СОЗДАТЬ АККАУНТ":"ВОЙТИ"}</button></form>{error&&<div className="error">{error}</div>}<button className="link" onClick={()=>setRegister(!register)}>{register?"У меня уже есть аккаунт":"Регистрация"}</button></div></main>
}
