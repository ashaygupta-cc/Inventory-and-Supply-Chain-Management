import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('Stockly_Comprehensive_Final_Report.tex', encoding='utf-8') as f:
    text = f.read()

# ── Step 1: Fix chapter / section numbering ───────────────────────────────────
# In report class, top level should be \chapter not \section
# Currently numbered sections are \section{...}, subsections are \subsection{...}, etc.

# We need to promote: section→chapter, subsection→section, subsubsection→subsection
# BUT ONLY for numbered ones (not starred)

numbered_sections = [
    'Introduction',
    'Requirement Analysis',
    'Design and Architecture',
    'Implementation Details',
    'Testing and Deployment',
    'Conclusion and Future Work',
    'Important Codebase References',
    'Code Listing Appendix',
]

# Temporarily tag starred sections to protect them
text = text.replace(r'\section*{', r'\STARRREDSEC{')

# Promote \section → \chapter (unnumbered sections already protected)
text = text.replace(r'\section{', r'\chapter{')

# Restore starred sections
text = text.replace(r'\STARRREDSEC{', r'\section*{')

# Promote \subsection → \section and \subsubsection → \subsection
text = text.replace(r'\subsubsection{', r'\TEMPSUBSUB{')
text = text.replace(r'\subsection{', r'\section{')
text = text.replace(r'\TEMPSUBSUB{', r'\subsection{')

print("Step 1 done: numbering fixed")

# ── Step 2: Update preamble to format \chapter titles nicely ─────────────────
# Find the titleformat section for \section and add \chapter format before it

old_chapter_fmt = r'''\titleformat{\section}
    {\color{sectionblue}\Large\bfseries}
    {\thesection}{1em}{}
    [\color{sectionblue}\titlerule]'''

new_chapter_fmt = r'''\titleformat{\chapter}[block]
    {\normalfont\huge\bfseries\color{sectionblue}}
    {\thechapter\quad}{0pt}{}
    [\vspace{-0.3em}\color{sectionblue}\rule{\textwidth}{0.6pt}]
\titlespacing*{\chapter}{0pt}{-15pt}{1.2em}

\titleformat{\section}
    {\color{sectionblue}\Large\bfseries}
    {\thesection}{1em}{}
    [\color{sectionblue}\titlerule]'''

text = text.replace(old_chapter_fmt, new_chapter_fmt)

print("Step 2 done: chapter title format added")

# ── Step 3: Find the Design and Architecture chapter and inject expanded content
# We need to expand: Use Case detailed, DFA detailed, NFR/Stereotypes detailed

# ─── Inject enhanced Use Case Details after Use Case Summary section ─────────
old_usecase_end = r'''\subsection{Use-Case Diagram}
\placeholderimage{Uml_daigram.png}{0.90}{UML Use-Case and Class Diagram for the Stockly inventory and supply chain management system.}'''

new_usecase_end = r'''\subsection{Detailed Use Case Descriptions}

The following table provides structured descriptions of the most important use cases, including actors, preconditions, main event flow, and postconditions.

\begin{longtable}{p{0.18\textwidth}p{0.72\textwidth}}
    \toprule
    \textbf{Attribute} & \textbf{UC-01: Place an Order} \\
    \midrule
    Actor & Client \\
    Precondition & Client is authenticated; at least one product is in stock. \\
    Main Flow & (1) Client browses the product catalogue. (2) Selects one or more products and specifies quantities. (3) Submits the order. (4) System validates available stock for every line item (fail-fast). (5) System creates the Order document with status \texttt{pending} and increments \texttt{reservedQuantity} for each product. (6) System auto-creates an Invoice with status \texttt{draft}. (7) Client receives a confirmation notification. \\
    Alternate Flow & If any item has insufficient stock, the entire order is rejected and no reservation is made. \\
    Postcondition & Order exists in \texttt{pending} status; reserved stock is held; invoice is in \texttt{draft} status. \\
    \bottomrule
\end{longtable}

\vspace{0.5em}

\begin{longtable}{p{0.18\textwidth}p{0.72\textwidth}}
    \toprule
    \textbf{Attribute} & \textbf{UC-02: Pay Invoice via Stripe} \\
    \midrule
    Actor & Client \\
    Precondition & An invoice exists with status \texttt{sent} or \texttt{draft}; Stripe is configured. \\
    Main Flow & (1) Client navigates to their invoice list and clicks Pay Now. (2) System calls \texttt{POST /api/payments/checkout} to create a Stripe Checkout Session. (3) Client is redirected to Stripe's hosted payment page. (4) Client completes payment on Stripe. (5) Stripe sends a \texttt{checkout.session.completed} webhook event to \texttt{POST /api/payments/webhook}. (6) Server verifies Stripe signature. (7) Server sets invoice status to \texttt{paid} and order \texttt{paymentStatus} to \texttt{paid}. \\
    Alternate Flow & If signature verification fails, the webhook is rejected with HTTP 400. \\
    Postcondition & Invoice status = \texttt{paid}; \texttt{paidAt} timestamp recorded; order \texttt{paymentStatus} = \texttt{paid}. \\
    \bottomrule
\end{longtable}

\vspace{0.5em}

\begin{longtable}{p{0.18\textwidth}p{0.72\textwidth}}
    \toprule
    \textbf{Attribute} & \textbf{UC-03: Transfer Stock Between Warehouses} \\
    \midrule
    Actor & Administrator \\
    Precondition & Source warehouse has sufficient allocated quantity for the product. \\
    Main Flow & (1) Admin selects source warehouse, destination warehouse, product, and quantity. (2) System validates that \texttt{sourceAllocation.quantity} $\geq$ requested quantity. (3) System creates a \texttt{StockTransfer} record with status \texttt{pending}. (4) System decrements source allocation and increments destination allocation atomically. (5) Transfer status is set to \texttt{completed}. \\
    Alternate Flow & If source has insufficient stock, transfer is rejected with HTTP 422 and status \texttt{cancelled}. \\
    Postcondition & Stock total for the product across all warehouses remains invariant. \\
    \bottomrule
\end{longtable}

\subsection{Use-Case Diagram}
\placeholderimage{Uml_daigram.png}{0.90}{UML Use-Case and Class Diagram for the Stockly inventory and supply chain management system.}'''

text = text.replace(old_usecase_end, new_usecase_end)
print("Step 3 done: detailed use case injected")

# ── Step 4: Expand the Activity Diagram, DFA, and NFR/Stereotypes sections ───

old_activity = r'''\section{Activity Diagram}

The activity diagram models the end-to-end behavioural workflow of Stockly across all user roles using swimlanes. It begins with user authentication, proceeds through role-specific decision points --- admin product management, client order placement, supplier dashboard access --- and terminates with order fulfilment and invoice settlement. Key decision nodes include stock availability checks, payment success/failure, and role-based content filtering.

\placeholderimage{activity_daigram.png}{0.90}{Activity Diagram showing system workflows across Admin, Supplier, and Client roles with swimlane decomposition.}'''

new_activity = r'''\section{Activity Diagram}

The Activity Diagram models the end-to-end behavioural workflow of Stockly across all user roles using UML swimlanes. Each swimlane represents one actor: \textbf{Client}, \textbf{Admin}, \textbf{Supplier}, and \textbf{System}. The diagram captures concurrent activity paths and key decision nodes.

\textbf{Client Swimlane:}
\begin{enumerate}
    \item Client opens the login page and submits credentials.
    \item System authenticates via JWT; on failure the client is shown an error.
    \item On success, the client lands on the catalogue and browses products.
    \item Client selects products, sets quantities, and submits order.
    \item System validates stock (decision node: \emph{stock sufficient?}).
    \item If sufficient, Stock is reserved and order created; if not, error is returned.
    \item Client is redirected to invoice and clicks Pay Now.
    \item System creates Stripe Checkout Session; client completes payment on Stripe.
    \item Stripe webhook fires; system marks invoice and order as paid.
\end{enumerate}

\textbf{Admin Swimlane:}
\begin{enumerate}
    \item Admin logs in and lands on the summary dashboard.
    \item Reviews low-stock alerts and manages products/categories.
    \item Confirms or cancels pending orders; system adjusts stock accordingly.
    \item Generates shipping labels via Shippo for shipped orders.
    \item Views revenue analytics and demand forecasting recommendations.
\end{enumerate}

\textbf{Supplier Swimlane:}
\begin{enumerate}
    \item Supplier logs in and lands on their scoped portal.
    \item Views product performance, orders containing their products, and low-stock alerts.
    \item No write access to orders or stock; read-only scoped view.
\end{enumerate}

\placeholderimage{activity_daigram.png}{0.90}{Activity Diagram showing system workflows across Admin, Supplier, and Client roles with swimlane decomposition.}'''

text = text.replace(old_activity, new_activity)
print("Step 4a done: activity diagram expanded")

# Expand DFA section
old_dfa = r'''\section{Data Flow Diagram}

The Data Flow Diagram (DFD) for Stockly describes how data moves between the user roles, the Next.js API back-end, the Prisma/MongoDB persistence layer, and the cache and event infrastructure. Clients submit booking requests that are validated and stored as Order documents; stock quantities are immediately updated. Administrators retrieve aggregated analytics data derived from the same underlying collections. Suppliers receive a read-only filtered view of orders that contain their products. The Redis cache layer intercepts read requests for frequently accessed resources and serves them without hitting MongoDB, significantly reducing latency for high-traffic endpoints.

\placeholderimage{Data Flow Architecture.png}{0.92}{Level-1 Data Flow Diagram for the Stockly system showing primary data flows between actors, processes, and stores.}'''

new_dfa = r'''\section{Data Flow Diagram}

The Data Flow Diagram (DFD) for Stockly describes how data moves between external entities, processing nodes, and data stores across two levels of decomposition.

\textbf{Level 0 --- Context Diagram:}

The system is treated as a single process labelled ``Stockly Application''. External entities are the three user roles --- Client, Supplier, and Admin --- and four external services: Stripe, Shippo, Brevo, and ImageKit. Data flows at this level include: (i) Clients send order requests and receive order confirmations and invoice payment links; (ii) Admins send configuration changes and receive analytics reports; (iii) Suppliers receive scoped product and order reports; (iv) Stripe sends webhook events and receives checkout session requests; (v) Shippo receives shipment creation requests and returns tracking data.

\textbf{Level 1 --- Process Decomposition:}

At Level 1 the application is decomposed into six major processes:

\begin{center}
\begin{tabularx}{\textwidth}{lXX}
    \toprule
    \textbf{Process} & \textbf{Input Flows} & \textbf{Output Flows} \\
    \midrule
    P1: Authentication & Login credentials from all roles & JWT session cookie \\
    P2: Product Management & Product CRUD requests from Admin & Product records to MongoDB; cache invalidation to Redis \\
    P3: Order Processing & Order create/update from Client/Admin & Stock reservation updates; invoice creation; shipping events \\
    P4: Invoice \& Payment & Invoice create from P3; webhook event from Stripe & Invoice records to MongoDB; email via Brevo \\
    P5: Analytics \& Forecasting & Read requests from Admin & Aggregated data from MongoDB; AI text from OpenRouter \\
    P6: Cache Layer & Read requests from P2--P5 & Cached JSON from Redis (TTL 2--30 min) \\
    \bottomrule
\end{tabularx}
\end{center}

\textbf{Data Stores:}

\begin{itemize}
    \item \textbf{DS1 --- MongoDB Atlas:} Persistent storage for all domain entities.
    \item \textbf{DS2 --- Upstash Redis:} Ephemeral cache for read-heavy queries and rate-limit counters.
    \item \textbf{DS3 --- ImageKit CDN:} Product images and QR code PNG files.
\end{itemize}

\placeholderimage{Data Flow Architecture.png}{0.92}{Level-1 Data Flow Diagram showing primary data flows between actors, processes, and stores in the Stockly system.}'''

text = text.replace(old_dfa, new_dfa)
print("Step 4b done: DFA expanded")

# Expand NFR / Stereotypes section
old_nfr_diag = r'''\section{Non-Functional Requirements and Stereotypes Diagram}

The NFR and Stereotypes diagram maps quality attributes to the system's architectural components using UML extension mechanisms. Stereotypes such as \texttt{$\langle\langle$cached$\rangle\rangle$}, \texttt{$\langle\langle$authenticated$\rangle\rangle$}, \texttt{$\langle\langle$rate-limited$\rangle\rangle$}, and \texttt{$\langle\langle$audited$\rangle\rangle$} are applied at the API route level to communicate which cross-cutting concerns are enforced. The diagram also documents the performance, security, and scalability requirements associated with each major system component, providing a visual traceability matrix between requirements and design decisions.

\placeholderimage{NFR and Stereotypes.jpeg}{0.90}{Non-Functional Requirements and UML Stereotypes Diagram showing cross-cutting concerns mapped to architectural components.}'''

new_nfr_diag = r'''\section{Non-Functional Requirements and Stereotypes Diagram}

\subsection{NFR Priority and Metrics Table}

The following table formalises each non-functional requirement with its priority (MoSCoW classification), the measurable metric used for verification, and the target value:

\begin{longtable}{p{0.06\textwidth}p{0.22\textwidth}p{0.10\textwidth}p{0.28\textwidth}p{0.22\textwidth}}
    \toprule
    \textbf{ID} & \textbf{Requirement} & \textbf{Priority} & \textbf{Metric} & \textbf{Target} \\
    \midrule
    \endhead
    NFR-1 & Response Performance & Must & p95 API response time & $\leq$ 500\,ms \\
    NFR-2 & Cache Efficiency & Must & Redis cache hit rate & $\geq$ 80\% for read endpoints \\
    NFR-3 & Password Security & Must & bcrypt cost factor & $\geq$ 10 rounds \\
    NFR-4 & Cookie Security & Must & \texttt{httpOnly}, \texttt{Secure}, \texttt{SameSite} flags & Set on all \texttt{session\_id} cookies \\
    NFR-5 & Rate Limiting & Should & Requests per window & 100 req / 15 min per IP \\
    NFR-6 & Availability & Should & Uptime (SLA) & 99.9\% monthly \\
    NFR-7 & Input Validation & Must & Zod schema coverage & 100\% of API POST/PATCH bodies \\
    NFR-8 & Auditability & Should & Audit log coverage & 100\% of write operations \\
    NFR-9 & Scalability & Could & Concurrent request capacity & 500 concurrent without degradation \\
    NFR-10 & Accessibility & Could & WCAG compliance level & 2.1 AA minimum \\
    \bottomrule
\end{longtable}

\subsection{UML Stereotypes in Stockly}

In UML, a \textbf{stereotype} is a mechanism for extending the vocabulary of UML by creating new model elements derived from existing ones. Stereotypes are denoted with double angle brackets: \texttt{$\langle\langle$name$\rangle\rangle$}. In Stockly's architecture, the following stereotypes are applied at the API layer to make cross-cutting concerns explicit and traceable:

\begin{center}
\begin{tabularx}{\textwidth}{lXX}
    \toprule
    \textbf{Stereotype} & \textbf{Meaning} & \textbf{Applied To} \\
    \midrule
    \texttt{$\langle\langle$authenticated$\rangle\rangle$} & Route requires a valid \texttt{session\_id} JWT cookie. Returns HTTP 401 if absent or expired. & All API routes except \texttt{/api/auth/login}, \texttt{/api/auth/register}, \texttt{/api/health} \\
    \texttt{$\langle\langle$authorised:admin$\rangle\rangle$} & Route additionally requires \texttt{role === "admin"}. Returns HTTP 403 otherwise. & Dashboard, warehouse delete, user management \\
    \texttt{$\langle\langle$cached$\rangle\rangle$} & Response is stored in Redis with a TTL before returning to the client. & Dashboard stats, product list, portal data, forecasting \\
    \texttt{$\langle\langle$rate-limited$\rangle\rangle$} & Number of requests from one IP per time window is capped. Returns HTTP 429 if exceeded. & Login, register, and all mutation endpoints \\
    \texttt{$\langle\langle$audited$\rangle\rangle$} & Every write operation creates an \texttt{AuditLog} record with userId, action, and timestamp. & Products, orders, invoices, warehouses, users \\
    \texttt{$\langle\langle$validated$\rangle\rangle$} & Request body is parsed through a Zod schema before any business logic executes. Returns HTTP 400 with field-level errors on failure. & All POST and PATCH endpoints \\
    \texttt{$\langle\langle$webhook$\rangle\rangle$} & Endpoint is called by an external service; signature verification is mandatory before processing. & \texttt{/api/payments/webhook} (Stripe) \\
    \bottomrule
\end{tabularx}
\end{center}

\subsection{Stereotype-to-Component Traceability}

\begin{center}
\begin{tabularx}{\textwidth}{lXXXXX}
    \toprule
    \textbf{Component} & \textbf{authn} & \textbf{authz} & \textbf{cached} & \textbf{rated} & \textbf{audited} \\
    \midrule
    Product list API & \checkmark & & \checkmark & \checkmark & \\
    Order create API & \checkmark & & & \checkmark & \checkmark \\
    Dashboard API & \checkmark & admin & \checkmark & & \\
    Login API & & & & \checkmark & \\
    Stripe webhook & & & & & \\
    Forecasting API & \checkmark & admin & \checkmark & & \\
    \bottomrule
\end{tabularx}
\end{center}

\placeholderimage{NFR and Stereotypes.jpeg}{0.90}{Non-Functional Requirements and UML Stereotypes Diagram showing cross-cutting concerns mapped to architectural components in Stockly.}'''

text = text.replace(old_nfr_diag, new_nfr_diag)
print("Step 4c done: NFR/Stereotypes expanded")

# ── Step 5: Expand Testing section with step-by-step and TikZ flowchart ──────

# Find the testing strategy section and inject expanded content with TikZ
old_testing_strategy = r'''\chapter{Testing and Deployment}

\section{Testing Strategy}

Testing in Stockly is structured as white-box testing, examining the internal logic of critical modules by exercising every identified branch, boundary condition, and error path. The strategy targets:
\begin{itemize}
    \item \textbf{85\% statement coverage} across all API route handlers and business logic modules.
    \item \textbf{90\% branch coverage} for security-critical paths (JWT verification, role checks) and financial logic (invoice totals, stock reservation).
    \item \textbf{100\% boundary coverage} for limit values such as stock quantity zero, invoice total floor, and rate-limit thresholds.
\end{itemize}

Testing is implemented with \textbf{Jest} for unit tests of pure functions and \textbf{Supertest} for API integration tests against a test MongoDB instance.

White-box testing examines internal code structure by:
\begin{itemize}
    \item identifying every decision branch in a function,
    \item designing test inputs that force each branch to execute,
    \item confirming database side-effects (e.g.\ no stock reserved when order fails),
    \item validating mathematical correctness of all financial calculations,
    \item ensuring security boundaries cannot be bypassed through internal logic.
\end{itemize}'''

new_testing_strategy = r'''\chapter{Testing and Deployment}

\section{Testing Strategy}

Testing in Stockly is structured as \textbf{white-box testing} --- a technique that examines the \emph{internal} code logic, branch paths, loops, and data transformations rather than only observable behaviour. The tester has complete access to the source code and designs inputs specifically to exercise every identified branch.

\textbf{Coverage targets:}
\begin{itemize}
    \item \textbf{85\% statement coverage} across all API route handlers and business logic modules.
    \item \textbf{90\% branch coverage} for security-critical paths (JWT verification, role checks) and financial logic (invoice totals, stock reservation).
    \item \textbf{100\% boundary coverage} for limit values such as stock quantity zero, invoice total floor, and rate-limit thresholds.
\end{itemize}

\textbf{Testing tools and infrastructure:}
\begin{itemize}
    \item \textbf{Jest} --- unit tests for pure functions (\texttt{verifyToken}, \texttt{calculateInvoiceTotal}, forecasting helpers).
    \item \textbf{Supertest} --- HTTP integration tests against a test MongoDB instance.
    \item \textbf{Stripe CLI} --- webhook simulation for payment event testing.
    \item \textbf{Prisma test client} --- ephemeral in-memory DB seeding and cleanup.
\end{itemize}

\textbf{General test procedure for each module:}
\begin{enumerate}
    \item \textbf{Setup:} Seed the test database with the minimum required documents (test user, test product, etc.).
    \item \textbf{Identify branches:} List every \texttt{if}/\texttt{else}, \texttt{try}/\texttt{catch}, and guard clause in the target function.
    \item \textbf{Design inputs:} For each branch, design a specific input that forces execution down that path.
    \item \textbf{Execute:} Run the test case via Jest / Supertest and capture the response.
    \item \textbf{Assert:} Verify HTTP status code, response body structure, and database side-effects.
    \item \textbf{Cleanup:} Delete all documents created during the test to ensure test isolation.
\end{enumerate}

\begin{center}
\begin{tabular}{clll}
    \toprule
    \textbf{Priority} & \textbf{Label} & \textbf{Scope} & \textbf{Must pass before} \\
    \midrule
    P1 & Critical & Auth, financial logic, security guards & Any release \\
    P2 & High & Core business logic, stock, RBAC & Sprint review \\
    P3 & Medium & Edge cases, format validation & QA sign-off \\
    P4 & Low & Informational / documentation & Documentation update \\
    \bottomrule
\end{tabular}
\end{center}'''

text = text.replace(old_testing_strategy, new_testing_strategy)
print("Step 5: testing strategy expanded")

# ── Add TikZ flowchart for Auth test flow right after Module 1 header ─────
old_auth_module_header = r'''\section{Module 1 --- Authentication}

\textbf{Source:} \texttt{utils/auth.ts}, \texttt{app/api/auth/login/route.ts}

The \texttt{verifyToken} function has five distinct branches, all of which must be covered:'''

new_auth_module_header = r'''\section{Module 1 --- Authentication}

\textbf{Source:} \texttt{utils/auth.ts}, \texttt{app/api/auth/login/route.ts}

\subsection{Step-by-Step Test Procedure for Login Endpoint}

The following sequence shows how a test engineer exercises every branch of the login flow:

\begin{enumerate}
    \item \textbf{Setup:} Insert a test user into MongoDB:
    \begin{lstlisting}[language={},caption={Test seed data}]
{ email: "admin@test.com",
  password: bcrypt.hashSync("correct123", 10),
  role: "admin" }
    \end{lstlisting}

    \item \textbf{Test AUTH-011 (Zod validation failure):}
    \begin{itemize}
        \item Input: \texttt{POST /api/auth/login} with body \texttt{\{ password: "x" \}} (email missing).
        \item Expected: HTTP \textbf{400}; body contains \texttt{error} describing the missing field.
        \item Branch covered: Zod schema \texttt{parse} throws \texttt{ZodError}.
    \end{itemize}

    \item \textbf{Test AUTH-012 (user not found):}
    \begin{itemize}
        \item Input: \texttt{POST /api/auth/login} with \texttt{\{ email: "ghost@x.com", password: "any" \}}.
        \item Expected: HTTP \textbf{401}; body \texttt{\{ error: "Invalid email or password" \}}.
        \item Branch covered: \texttt{prisma.user.findUnique} returns \texttt{null}.
    \end{itemize}

    \item \textbf{Test AUTH-013 (corrupted user data):}
    \begin{itemize}
        \item Input: Mock \texttt{findUnique} to return \texttt{\{ id: "x", password: null \}}.
        \item Expected: HTTP \textbf{500}; body \texttt{\{ error: "User data corrupted" \}}.
        \item Branch covered: \texttt{!user.password} guard.
    \end{itemize}

    \item \textbf{Test AUTH-014 (wrong password):}
    \begin{itemize}
        \item Input: \texttt{\{ email: "admin@test.com", password: "wrongpass" \}}.
        \item Expected: HTTP \textbf{401}; body \texttt{\{ error: "Invalid email or password" \}}.
        \item Branch covered: \texttt{bcrypt.compare} returns \texttt{false}.
    \end{itemize}

    \item \textbf{Test AUTH-014b (correct credentials --- happy path):}
    \begin{itemize}
        \item Input: \texttt{\{ email: "admin@test.com", password: "correct123" \}}.
        \item Expected: HTTP \textbf{200}; \texttt{Set-Cookie} header with \texttt{session\_id=<jwt>; HttpOnly; Secure; SameSite=Strict}.
        \item Branch covered: Full happy path (Branch E of \texttt{verifyToken}).
    \end{itemize}

    \item \textbf{Cleanup:} Delete test user from MongoDB.
\end{enumerate}

\subsection{Login Route Decision Tree}

The control flow through the login route handler covers the following branches:

\begin{center}
\begin{tabular}{clp{7cm}}
    \toprule
    \textbf{Node} & \textbf{Condition} & \textbf{Outcome} \\
    \midrule
    D1 & Request body is valid JSON object? & No $\to$ 400; Yes $\to$ D2 \\
    D2 & Zod schema validates email + password? & No $\to$ 400; Yes $\to$ D3 \\
    D3 & User found in database? & No $\to$ 401; Yes $\to$ D4 \\
    D4 & \texttt{user.password} is non-null? & No $\to$ 500; Yes $\to$ D5 \\
    D5 & \texttt{bcrypt.compare} returns true? & No $\to$ 401; Yes $\to$ D6 \\
    D6 & JWT token generated successfully? & No $\to$ 500; Yes $\to$ 200 + cookie \\
    \bottomrule
\end{tabular}
\end{center}

The \texttt{verifyToken} function has five distinct branches, all of which must be covered:'''

text = text.replace(old_auth_module_header, new_auth_module_header)
print("Step 5b: auth test procedure added")

# ── Add step-by-step for Order module ────────────────────────────────────────
old_ord_header = r'''\section{Module 2 --- Order Management and Stock State Machine}

\textbf{Source:} \texttt{app/api/orders/route.ts}, \texttt{prisma/order.ts}

The stock reservation logic is the most critical business-logic path in the system. All branches of the fail-fast validation loop must be covered:'''

new_ord_header = r'''\section{Module 2 --- Order Management and Stock State Machine}

\textbf{Source:} \texttt{app/api/orders/route.ts}, \texttt{prisma/order.ts}

\subsection{Step-by-Step Test Procedure for Order Creation}

\begin{enumerate}
    \item \textbf{Setup:} Seed Product A: \texttt{\{quantity: 15, reservedQuantity: 8\}} (availableStock = 7).
    \item \textbf{Test ORD-003 (product not found):}
        \begin{itemize}\item Input: order with \texttt{productId: "nonexistent"}. Expected: thrown error ``Product not found''.\end{itemize}
    \item \textbf{Test ORD-004 (insufficient stock):}
        \begin{itemize}\item Input: \texttt{quantity: 10}. Internal: $15 - 8 = 7 < 10$. Expected: thrown error ``Insufficient stock. Available: 7, Requested: 10''. \textbf{Assert:} \texttt{reservedQuantity} remains 8 (no side-effect).\end{itemize}
    \item \textbf{Test ORD-005 (boundary --- exactly enough):}
        \begin{itemize}\item Input: \texttt{quantity: 7}. Expected: order created successfully. \textbf{Assert:} \texttt{reservedQuantity} becomes 15 (8 + 7).\end{itemize}
    \item \textbf{Test ORD-006 (boundary + 1):}
        \begin{itemize}\item Input: \texttt{quantity: 8}. Expected: error (7 < 8).\end{itemize}
    \item \textbf{Test ORD-008 (multi-item atomicity):}
        \begin{itemize}\item Input: two items; first valid, second insufficient. Expected: error on second item; \textbf{no} reservation for first item --- confirms fail-fast pre-validation.\end{itemize}
    \item \textbf{Test ORD-010 (cancel pending order):}
        \begin{itemize}\item After creating a pending order, send \texttt{PATCH} with \texttt{status: "cancelled"}. Assert: \texttt{reservedQuantity} decremented back to 8.\end{itemize}
    \item \textbf{Cleanup:} Delete test products and orders.
\end{enumerate}

The stock reservation logic is the most critical business-logic path in the system. All branches of the fail-fast validation loop must be covered:'''

text = text.replace(old_ord_header, new_ord_header)
print("Step 5c: order test procedure added")

# ── Save the final file ───────────────────────────────────────────────────────
with open('Stockly_Comprehensive_Final_Report.tex', 'w', encoding='utf-8') as f:
    f.write(text)

lines = text.splitlines()
print(f'\nFinal file: {len(lines)} lines')
print('Balanced:', text.count(r'\begin{') == text.count(r'\end{'))
print('end{document}:', text.count(r'\end{document}'))

# Verify chapter numbering
import re
chapters = re.findall(r'\\chapter[*]?\{([^}]+)\}', text)
print(f'\nChapters ({len(chapters)}):')
for i, c in enumerate(chapters):
    star = '*' if f'\\chapter*{{{c}}}' in text else ' '
    print(f'  [{star}] {c}')
