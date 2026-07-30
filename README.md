# BlogWebsite
A FullStack Webstie

Sprint-1:
Got it — now the whole vision is **very clear**.
Let me restate the project exactly as you described it, then I’ll give you the exact **next steps for YOUR FRIEND’S login + home-page control system**.

---

# 🎯 **PROJECT SUMMARY (Your Words → Structured Format)**

## ✅ **This project is a blog/social-media style site for your friend.**

* Think **Instagram + Blog** hybrid.
* Visitors can **view posts, like posts, comment**, but cannot create posts.
* Only **your friend** (the creator) can log in and create posts.
* There is one **Admin** (you or someone else) who logs in separately to moderate comments.

---

# 🧑‍💻 **There are exactly 2 types of users:**

## **1️⃣ Your Friend (“Content Creator”)**

He logs in to:

* Create posts
* Upload pictures
* Write text boxes
* Edit the home page welcome message
* Manage his posts
* Delete his posts
* Change display style of homepage sections

Everything the visitor sees on the home page is controlled by this user.

---

## **2️⃣ Admin (“Comment Moderator”)**

This user logs in to:

* See all comments
* Approve or reject comments before they go live
* Remove toxic comments
* Block certain users/IPs if needed (optional future feature)

Admin **cannot create posts**, only moderate comments.

---

# 👀 **Visitors (No Login)**

They can:

* View posts
* Like posts
* Write comments (pending approval)
* View the welcome message
* View image + text posts

They cannot:

* Log in
* Create posts
* Edit anything
* Approve comments

---

# 🔥 **WHAT WE ARE BUILDING *RIGHT NOW***

You said:

> “Before we go any further in this scrum I want to build the part where I create my friend's login, and let this login page control how the home page looks like.”

So our immediate sprint deliverables 👉

---

# 🚀 **SPRINT 1 DELIVERABLES — Creator Login + Home Page Control**

We are ONLY building:

### **✔ Creator Login Page**

### **✔ JWT authentication (already built on backend)**

### **✔ Creator Dashboard**

A page your friend sees after login.

### **✔ “Home Page Control Panel”**

A UI where your friend can:

* Change the Home Page Welcome Message
* Add/Upload Post Pictures
* Add Text Posts
* Save/Publish Posts

### **✔ Home Page Rendering**

The homepage should automatically pull:

* The welcome message
* All posts (image + text)
* Display them for visitors

---

# 💻 **SPRINT 1 STRUCTURE**

### **Backend (Django) Needed**

* `/api/auth/login/` (done)
* `/api/posts/create/`
* `/api/posts/list/`
* `/api/posts/delete/`
* `/api/homepage/welcome/` (to edit welcome message)

### **Frontend (Next.js) Needed**

* `/auth/login`
* `/creator/dashboard`
* `/creator/posts/new`
* `/creator/homepage-settings`
* `/` (public homepage showing posts)

---

# 🧱 **NEXT STEP (RIGHT NOW):**

### 👉 We build your Friend’s **Creator Login + Dashboard**

After login, your friend must go to a dashboard like:

```
/creator/dashboard
```

This dashboard will have:

* Button: “Edit Welcome Message”
* Button: “Create New Post”
* Button: “View My Posts”

Then we build the homepage to reflect what he posts.

---

# ❤️ **Before I write ANY code**

I need one confirmation from you:

# ❓ **Do you want the friend and admin to be separate user types?**

Choose one:

### **Option A — YES, two user roles**

* Role: `creator` (your friend)
* Role: `admin` (comment moderator)

### **Option B — NO, only your friend logs in right now**

Admin role can be added later.

---

**Which option should I build?**
