// Load Supabase JS library if not already loaded
if (!window.supabase) {
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js";
    script.onload = initializeSupabase;
    document.head.appendChild(script);
  } else {
    initializeSupabase();
  }
  
  // Initialize Supabase using configuration from the server
  function initializeSupabase() {
    fetch("/config")
      .then(response => response.json())
      .then(config => {
        if (!config.SUPABASE_URL || !config.SUPABASE_KEY) {
          throw new Error("Missing Supabase config");
        }
        window.supabase = supabase.createClient(config.SUPABASE_URL, config.SUPABASE_KEY);
        console.log("Supabase initialized:", config.SUPABASE_URL);
      })
      .catch(error => console.error("Error fetching config:", error));
  }
  
  // Wait until Supabase is initialized
  async function waitForSupabase() {
    while (!window.supabase) {
      await new Promise(resolve => setTimeout(resolve, 100)); // Wait 100ms
    }
  }
  
  // Sign up function for new users
  async function signUp() {
    await waitForSupabase();
    
    const username = document.getElementById("username")?.value.trim();
    const name = document.getElementById("name")?.value.trim();
    const phoneno = document.getElementById("phone")?.value.trim();
    const password = document.getElementById("password")?.value;
    const confirmPassword = document.getElementById("confirm-password")?.value;
  
    if (!username || !name || !phoneno || !password || !confirmPassword) {
      alert("Please fill out all fields!");
      return;
    }
    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
  
    const { data, error } = await supabase.auth.signUp({
      email: username + "@example.com",
      password: password
    });
    if (error) {
      console.error("Sign-up error:", error.message);
      alert("Error signing up: " + error.message);
      return;
    }
  
    const user = data.user;
    if (user) {
      const { error: dbError } = await supabase
        .from("users")
        .insert([
          {
            id: user.id,
            username: username,
            name: name,
            phoneno: phoneno,
            password: password
          }
        ]);
      if (dbError) {
        console.error("Database insert error:", dbError.message);
        alert("Error saving user details: " + dbError.message);
        return;
      }
      alert("Sign-up successful! Redirecting to login.");
      window.location.href = "login.html";
    }
  }
  
  // Login function for existing users
  async function login() {
    await waitForSupabase();
    
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
  
    const { user, error } = await supabase.auth.signInWithPassword({
      email: username + "@example.com",
      password: password
    });
    if (error) {
      console.error("Login error:", error.message);
      alert("Error logging in: " + error.message);
    } else {
      alert("Login successful!");
      window.location.href = "sel_page.html";
    }
  }
  
  // Expose functions to the global scope
  window.signUp = signUp;
  window.login = login;
  