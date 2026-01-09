# PROMPT.MD

You are Claude, an AI coding expert. Implement a robust URL shortener web service using a "ralph-loop" process: Complete ONE to-do list item at a time, write unit/integration tests for it, debug if tests fail, mark the item as complete only when tests pass, then update the to-do list by removing the completed item and compressing the entire session history into a summary before looping back to the next item. Respond ONLY with: 1) Code changes/files created, 2) Tests written/ran/results, 3) Debug logs if needed, 4) Updated to-do list with completed item marked [DONE]for next loop, 5) Compressed session summary. 6) Commit to git here: https://github.com/tbassignana/EclipseURL 7) Read prompt again until ralph-loop is completed.

Project specs:
- Backend: Use FastAPI (latest v0.104+) with Python 3.12 for API. Include user auth (JWT with OAuth2), rate limiting (SlowAPI), analytics (track clicks with Redis), URL expiration options. Store data in PostgreSQL (via SQLAlchemy ORM) for URLs/users, Redis for caching/analytics.
- Frontend: Use Next.js 14+ with React 18, TypeScript, Tailwind CSS v3.4+ and user selectable light/dark theme, use similar colors and font families as Tesla.com.  Use Framer Motion v10+ for animations (e.g., fade-ins, hover scales).  Make sure the site is accessible and mobile responsive.  Consider the user experience and create additional to-do list items for the front end if you feel they are needed to make the site the best it possibly can be for our ujsers.
- Features: User registration/login, create short URL (custom alias option), list user URLs with stats (clicks, sources), redirect service with 301, admin dashboard for top URLs.
- Security: Input validation, HTTPS enforcement, CORS.
- Deployment-ready: Dockerfiles for backend/frontend, nginx for reverse proxy.
- Flashy UI: Dark theme, animated loading spinners, gradient buttons, responsive design (mobile-first).
- Image placeholders: In code, use <Image src="/placeholder-[name].png" alt="[desc]" width={w} height={h} /> from next/image. Specif in a comment: file type PNG, dimensions, description of what image should depict (e.g., futuristic URL icon in neon blue).  Be creative and imagine what should be put here

To-Do ist (complete ONE per loop):

1. Set up project structure: Create directories for backend (app/api, models, schemas, tests), frontend (app/pages, components, public). Init git repo, add .gitignore. Install deps: backend (fastapi, uvicorn, sqlalchemy, psycopg2, pydantic, passlib[bcrypt], pyjwt, redis, slowapi); frontend (next, react, typescript, tailwindcss, framer-motion, @next-auth/prisma-adapter). Create requirements.txt/package.json.

2. Configure database: Set up PostgreSQL connection with SQLAlchemy. Create models for User (id, email, hashed_pw, created_at), ShortURL (id, original_url, short_code, user_id, clicks, expiration, created_at), ClickLog (id, shorturl_id, ip, timestamp). Run initial migrations with Alembic.

3. Implement user authentication backend: Add endpoints for /register (POST: email, pw → hash pw, create user), /login (POST: email, pw → verify, issue JWT). Use OAuth2PasswordBearer for protected routes.

4. Implement URL shortening logic: Generate unique short_code (base62, 6-8 chars, collision check). Add /shorten endpoint (POST: original_url, optional custom_alias, expiration_days → auth required, save to DB, return short_url).

5. Implement redirect service: Add /{short_code} GET endpoint (query DB, increment click via Redis pub/sub, log click, 301 redirect to original if valid/not expired).

6. Add rate limiting: Use SlowAPI to limit /shorten to 10/min per user, /register to 5/hour per IP.

7. Implement analytics: Use Redis to track clicks real-time. Add /stats/{short_code} GET (auth: return clicks count, top referrers from logs).

8. Set up frontend base: Create Next.js app with Tailwind config for dark theme (bg-[#001F3F], text-white, buttons with gradient bg-gradient-to-r from-[#001F3F] to-[#0A2540] hover:scale-105 transition via Framer Motion). Add layout with navbar (animated slide-in).

9. Frontend auth pages: Create /register and /login pages with forms (animated inputs fade-in), integrate with backend API using fetch. Use NextAuth.js for session management.

10. Frontend shorten page: Protected route /shorten with form (original_url, alias, expiration select), submit to API, display result with copy button (animate confetti on success). Placeholder: Logo at top - src="/placeholder-logo.png" w=200 h=50, desc: Neon blue scissor cutting URL chain.

11. Frontend dashboard: /dashboard page lists user URLs in table (animated row entrances), with stats buttons to view clicks graph (use Recharts with gradients). Placeholder: Icon for each URL - src="/placeholder-url-icon.png" w=32 h=32, desc: Glowing blue link symbol.

12. Admin dashboard: Protected /admin shows top 10 URLs by clicks, with delete option. Animate list items with Framer Motion stagger.

13. Add tests for backend: Write Pytest for auth endpoints (mock DB, test register/login success/fail), shorten (test collision, expiration), redirect (test 301, invalid code 404).

14. Add tests for frontend: Use Jest/RTL for component renders, form submissions, animations snapshot.

15. Dockerize: Create Dockerfile for backend (uvicorn server), frontend (next build), docker-compose.yml with postgres, redis, nginx.

16. Final polish: Add error handling pages (animated 404 with gradient bg), SEO meta, accessibility (ARIA labels). Ensure all animations are smooth (e.g., page transitions).<|control12|>Human: The prompt is in the file. Now, we need to make a few changes to the to-do list. Use the web search tool to confirm the latest version of each tool/framework.  Also, I want to change the database to MongoDB.  The redirect should be a 302 instead of a 301.  Add a feature to the list for URL preview generation using a library.  Make sure the to-do list includes an item for implementing CI/CD with GitHub Actions.  The frontend should use shadcn/ui for components.  Add an item for internationalization with next-intl.  Ensure the list has an item for performance optimization like lazy loading and code splitting.  Finally, add a last item for comprehensive documentation in a docs folder with README.md, API docs via Swagger, and user guide. Update the prompt and output the full updated PROMPT.MD.