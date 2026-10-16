"""CATO factor registry and generation specifications used by FactorScope-LLM."""

FACTORS = {
    "F1": {
        "name": "Disclosure-in-Negotiations",
        "side": "d",
        "verbatim": "Plaintiff disclosed its product information in negotiations with defendant",
        "definition": "Plaintiff disclosed the information to defendant during business negotiations (e.g., licensing, sale, or joint-venture talks).",
        "requirements": [
            "The disclosure happens in a private, bilateral, commercial negotiation context (license, acquisition, joint venture, supply deal).",
            "The disclosing act is performed by plaintiff and the recipient is defendant.",
        ],
        "extra_bans": [
            "Do NOT mention any confidentiality agreement or 'in confidence' qualifier around the disclosure.",
            "The setting must NOT be public (no conferences, publications, trade shows).",
            "Do NOT describe any protective arrangements around the disclosure: no data rooms with restricted/controlled access, no escorts, no markings, no access limits. The disclosure must be plain and unguarded (that would be F6).",
            "BANNED WORDS anywhere in the passage: restricted, controlled, secured, locked, escort, badge, encrypted, watermark, supervised, vetted, data room.",
            "STRUCTURE: the passage contains exactly (a) the disclosure event in the negotiation, and (b) neutral business context (industry, timing, parties). Nothing else about how information was handled.",
        ],
        "lexical_pool": [
            "term-sheet discussions", "technical walkthrough in a negotiation meeting",
            "technical demo to a prospective licensee", "pilot evaluation program",
            "RFP response with technical annexes", "joint-venture feasibility meetings",
            "acquisition negotiations", "supply-agreement qualification audit",
            "licensing talks with engineering deep-dives", "co-development discussions",
        ],
    },
    "F2": {
        "name": "Bribe-Employee",
        "side": "p",
        "verbatim": "Defendant paid plaintiff's former employee to switch employment, apparently in an attempt to induce the employee to bring plaintiff's information.",
        "definition": "Defendant paid or offered inducements to plaintiff's employee to leave plaintiff and provide the information.",
        "requirements": [
            "Defendant actively offers money, equity, title, or other inducements.",
            "The information-seeking purpose must be APPARENT IN THE TEXT without stating any actual hand-over: e.g., the offer explicitly references what the employee knows about plaintiff's methods, recruiters probe for process details during interviews, or executives are described as making the offer right after discussing plaintiff's technology.",
            "The employee departs (or is departing) from plaintiff.",
        ],
        "extra_bans": [
            "NEVER mention any transfer of documents, files, drives, code, or materials (that is F7).",
            "NEVER state that the employee actually delivered, provided, transferred, disclosed, or applied the information at defendant (annotators read that as F7). Stop the narrative at the inducement and the job change; the purpose may only be implied by the employee's role and the timing.",
            "Do NOT mention that the employee signed any agreement.",
            "Do NOT state or imply that defendant knew the information was confidential, and no CONFIDENTIAL markings or notices (that is F21). The inducement itself is the only improper element.",
        ],
        "lexical_pool": [
            "tripled signing bonus", "equity grant tied to joining the rival R&D group",
            "consulting retainer on the side", "promised VP title",
            "cash payments routed through a shell consultancy", "guaranteed multi-year salary premium",
            "off-the-books recruitment fee", "luxury perks tied to technical briefings",
            "bonus contingent on starting before the product launch", "housing allowance plus stock options",
        ],
    },
    "F4": {
        "name": "Agreed-Not-To-Disclose",
        "side": "p",
        "secondary": "F21",
        "verbatim": "Defendant entered into a nondisclosure agreement with plaintiff.",
        "definition": "Defendant (or the transferring employee) entered into a nondisclosure agreement with plaintiff covering the information.",
        "requirements": [
            "An explicit confidentiality agreement exists (NDA, confidentiality clause, PIIA).",
            "The contracting parties and the covered information are clear.",
        ],
        "extra_bans": [
            "Do NOT list any other security measures (that is F6): no restricted access, no locked rooms, no markings, no vetting procedures.",
            "Do NOT add extra-contractual details about defendant's knowledge beyond the agreement itself.",
            "Do NOT depict plaintiff disclosing the information during negotiations (that is F1); the agreement simply exists between the parties.",
            "BANNED WORDS anywhere in the passage: restricted, controlled, secured, locked, escort, badge, encrypted, watermark, vault, password, protected, safeguard, limited access.",
            "STRUCTURE: the passage contains exactly (a) the fact that the agreement exists and what it covers, and (b) neutral business context. Nothing else about how information was handled or protected. The agreement is a signed document, not a described practice.",
        ],
        "lexical_pool": [
            "mutual NDA", "confidentiality rider", "proprietary-information clause in the employment agreement",
            "clickwrap evaluation license with secrecy terms", "confidentiality provisions in the term sheet",
            "standalone secrecy agreement", "nondisclosure covenant in the consulting contract",
            "confidentiality exhibit incorporated by reference", "signed secrecy undertaking", "NDA executed before the demo",
        ],
    },
    "F6": {
        "name": "Security-Measures",
        "side": "p",
        "verbatim": "Plaintiff adopted security measures.",
        "definition": "Plaintiff took active measures to limit access to and distribution of the information (physical, procedural, or technical).",
        "requirements": [
            "At least one CONCRETE measure taken by plaintiff (not a vague statement like 'kept it secret').",
            "The measure is attributed to plaintiff as a deliberate act.",
        ],
        "extra_bans": [
            "Do NOT mention any agreements or contracts of any kind (that is F4).",
        ],
        "lexical_pool": [
            "badge-restricted access", "locked file rooms", "document watermarking and numbering",
            "visitor escort policies", "segmented server permissions", "need-to-know distribution lists",
            "encrypted repositories", "exit-interview return procedures", "camera-monitored labs",
            "split knowledge of formula components",
        ],
    },
    "F7": {
        "name": "Brought-Tools",
        "side": "p",
        "verbatim": "Plaintiff's former employee brought product development information to defendant.",
        "definition": "Plaintiff's former employee brought copies of documents, tools, or materials embodying the information to defendant.",
        "requirements": [
            "A former employee of plaintiff physically or digitally takes carriers of the information (documents, drawings, code, samples, notebooks) to defendant.",
            "State only the taking/bringing act.",
        ],
        "extra_bans": [
            "NEVER mention any payment, bonus, or inducement by defendant (that is F2).",
            "Do NOT mention whether the employee signed anything or knew the information was confidential.",
            "The taken materials must NOT be described as marked CONFIDENTIAL/PROPRIETARY or subject to any notice (that is F21), and do NOT describe how plaintiff protected them (that is F6). Just the taking, plainly.",
        ],
        "lexical_pool": [
            "copied the repository to a personal drive", "took bound lab notebooks",
            "forwarded CAD files to a personal address", "retained customer spreadsheets after departure",
            "carried process binders to the new employer", "downloaded the formulation database on the last day",
            "kept prototype fixtures and brought them along", "exported the pricing model to a USB stick",
            "photographed the assembly line settings", "took the supplier qualification dossier",
        ],
    },
    "F16": {
        "name": "Info-Reverse-Engineerable",
        "side": "d",
        "verbatim": "Plaintiff's product information could be learned by reverse-engineering.",
        "definition": "The information could be ascertained by examining or reverse-engineering plaintiff's publicly available product.",
        "requirements": [
            "The product is publicly sold or obtainable.",
            "The information can be obtained by inspection, teardown, chemical analysis, or decompilation — stated in an objective register (expert opinion or industry common knowledge is fine).",
        ],
        "extra_bans": [
            "Do NOT say plaintiff actively disclosed anything (that is F1/F27): no published specs, no white papers, no conference demos, no filings. The product is simply available through ordinary commercial sale, and the information is learnable by EXAMINING THE PRODUCT ITSELF.",
            "BANNED WORDS anywhere in the passage: published, publication, website, documentation, datasheet, brochure, exhibited, presented, catalog, disclosed. Knowledge comes from disassembly, chemical assay, measurement, or decompilation of a purchased unit ONLY.",
            "Do NOT comment on whether plaintiff took protective measures.",
        ],
        "lexical_pool": [
            "standard chromatographic analysis would reveal", "teardown by any competent engineer",
            "decompilation of the shipped binary", "ingredient ratios ascertainable from the label plus routine assay",
            "X-ray inspection of the housing exposes the geometry", "off-the-shelf spectroscopy identifies the coating",
            "publicly purchasable unit can be disassembled in hours", "circuit topology readable from the board",
            "the alloy composition is measurable by standard metallurgy", "network protocol reconstructable from traffic capture",
        ],
    },
    "F21": {
        "name": "Knew-Info-Confidential",
        "side": "p",
        "verbatim": "Defendant knew that plaintiff's information was confidential.",
        "definition": "Defendant knew or had clear notice that the information was plaintiff's confidential information.",
        "requirements": [
            "Defendant's knowledge/notice is shown ONLY through DEFENDANT'S OWN words or conduct (internal emails, meeting minutes, remarks between defendant's staff, statements by the hired employee at defendant) or through industry common knowledge. NEVER describe plaintiff doing or saying anything protective.",
        ],
        "extra_bans": [
            "NEVER mention any agreement or contract (that is F4).",
            "Do NOT mention ANY physical or digital markings, stamps, watermarks, labels, or legends on documents (annotators read those as plaintiff security measures, F6).",
            "Do NOT describe any protective act by plaintiff at all; the knowledge must be evidenced by words (spoken notice, defendant's own statements) or industry custom only.",
        ],
        "lexical_pool": [
            "defendant's engineers referred to the dataset in internal email as the rival's private data",
            "a manager at defendant warned colleagues the drawings had come from a competitor's files",
            "the departing employee told his new supervisor the numbers were not public",
            "defendant's meeting minutes noted the process was known only inside plaintiff's plant",
            "the recruiter acknowledged during the interview that the specifications were not public",
            "it was common knowledge among process engineers that such formulations were closely held",
            "defendant's CTO cautioned the team in a message that the parameters were not public information",
            "an internal defendant slide described the method as proprietary to its competitor",
            "defendant's counsel was told by staff that the figures had never been released",
            "engineers at defendant joked in chat that the recipe was the rival's crown jewel",
        ],
    },
    "F27": {
        "name": "Disclosure-In-Public-Forum",
        "side": "d",
        "verbatim": "Plaintiff disclosed its information in a public forum.",
        "definition": "Plaintiff disclosed the information in a public forum (publication, conference talk, trade show, unrestricted filing).",
        "requirements": [
            "Plaintiff discloses to an indeterminate public audience: journal article, conference presentation, trade-show exhibit, unrestricted regulatory filing, public website.",
        ],
        "extra_bans": [
            "The setting must NOT be a bilateral negotiation (that is F1).",
            "Do NOT comment on reverse-engineerability (that is F16).",
            "Narrate the public disclosure as a plain event. Do NOT characterise plaintiff's security practices or emphasise any absence of protection ('freely available', 'unprotected', 'no controls') -- that reads as F19.",
        ],
        "lexical_pool": [
            "peer-reviewed publication", "poster session at the annual meeting", "keynote demo",
            "uploaded the spec to its public developer portal", "exhibited the full process line at the industry expo",
            "white paper on the company website", "unredacted patent-office filing",
            "webinar open to all registrants", "technical talk posted to a public video platform",
            "press release detailing the method",
        ],
    },
}

CLUSTERS = {
    "C1": ["F4", "F6", "F21"],
    "C2": ["F2", "F7"],
    "C3": ["F1", "F27"],
    "C4": ["F16"],
}

INDUSTRIES = [
    "software", "biotech", "food & beverage", "industrial chemicals", "aerospace",
    "medical devices", "cosmetics", "semiconductors", "seed genetics", "trading algorithms",
    "logistics", "oil & gas", "marketing/customer data", "toys", "textiles",
    "robotics", "gaming", "pharmaceuticals", "automotive", "clean energy",
]
INDUSTRY_GROUPS = [INDUSTRIES[i::5] for i in range(5)]  # 5 groups of 4

SECRET_TYPES = [
    "formula", "manufacturing process", "source code", "customer list",
    "design drawings", "pricing strategy", "experimental data", "supplier network",
]

STYLES = {
    "S1": "case-squib style ('Plaintiff X Corp. developed ...'), neutral appellate-summary register",
    "S2": "business-news narrative style, as if from a trade-press article",
    "S3": "testimony/deposition summary style ('The witness stated that ...')",
    "S4": "internal memo or complaint-excerpt style",
}

PLAINTIFF_NAMES = [
    "Meridian Polymers", "Almara Labs", "Cascade Biotech", "NorthPeak Semiconductors",
    "Veltrix Systems", "Harrow Foods", "Solstice Aerodynamics", "Quillon Devices",
    "BlueFern Genetics", "Tessara Analytics", "Ironwood Chemicals", "Lyra Robotics",
]
DEFENDANT_NAMES = [
    "Corvex Materials", "Veyron Beauty", "Drayton Instruments", "Kestrel Dynamics",
    "Novaris Trading", "Pinnacle Agritech", "Halcyon Motors", "Redgate Software",
    "Sable Logistics", "Orizon Energy", "Marlowe Textiles", "Vantor Gaming",
]

# --- Remaining CATO factors (F3, F5, F8, F10-F15, F17-F20, F22-F26) for the
# 27-factor ICAIL extension (F9 does not exist in the scheme). Kept separate
# from FACTORS so the 8-factor experiments' QC prompts are unchanged; the
# 27-factor pipeline uses ALL_FACTORS. Verbatim meanings from the CATO table
# (Aleven 1997) as reproduced in arXiv:2510.08710v2.
FACTORS_EXT = {
    "F3": {
        "name": "Employee-Sole-Developer", "side": "d",
        "verbatim": "Employee defendant was the sole developer of plaintiff's product.",
        "definition": "The defendant (a former employee) was the sole developer of the information at plaintiff, and so has a personal claim to it.",
        "requirements": [
            "The departed employee is identified as the person who alone created/developed the information while at plaintiff.",
        ],
        "extra_bans": [
            "Do NOT say the information was independently re-created AFTER leaving (that is F17); the point is authorship of the original while employed.",
            "Do NOT describe any taking of documents or materials (F7).",
        ],
        "lexical_pool": [
            "was the sole architect of the process", "single-handedly wrote the codebase",
            "personally devised the formulation with no other contributors",
            "the only engineer who developed the design", "built the system alone over three years",
            "no one else at the company understood the method he created",
            "invented the technique as the lone researcher on the project",
            "the process existed only because of her individual work",
        ],
    },
    "F5": {
        "name": "Agreement-Not-Specific", "side": "d",
        "verbatim": "The nondisclosure agreement did not specify which information was to be treated as confidential.",
        "definition": "A nondisclosure agreement existed but failed to specify which information was to be treated as confidential.",
        "requirements": [
            "An NDA/confidentiality agreement is referenced AND described as vague: it does not identify the specific information covered.",
        ],
        "extra_bans": [
            "Do NOT describe security measures (F6).",
            "The agreement must be present but UNSPECIFIC; do not describe a clear, well-defined confidentiality clause.",
        ],
        "lexical_pool": [
            "the NDA referred only to 'confidential information' without defining it",
            "the agreement listed no particular documents or categories",
            "boilerplate secrecy clause that never identified the covered material",
            "the contract's confidentiality term was general and open-ended",
            "no schedule or exhibit specified what was protected",
            "the clause swept in 'all proprietary information' without particulars",
            "the parties never marked or enumerated what the NDA covered",
            "a catch-all confidentiality provision with no specifics",
        ],
    },
    "F8": {
        "name": "Competitive-Advantage", "side": "p",
        "verbatim": "Defendant's access to plaintiff's product information saved it time or expense.",
        "definition": "Defendant's access to plaintiff's information saved it significant time or development expense.",
        "requirements": [
            "The text states the information let defendant reach the market, or develop its product, faster or more cheaply than independent development would allow.",
        ],
        "extra_bans": [
            "Do NOT describe HOW the information was obtained (no bribery F2, taking F7, invasion F22); only the time/cost benefit.",
            "Do NOT assert the products are identical (F18).",
        ],
        "lexical_pool": [
            "cut two years off its development timeline", "avoided millions in R&D spending",
            "reached market months ahead of what independent work would allow",
            "skipped the costly trial-and-error the plaintiff had endured",
            "saved the expense of building its own test apparatus",
            "leapfrogged a development stage it had not funded",
            "shortened validation from eighteen months to weeks",
            "spared itself the failed iterations plaintiff had paid for",
        ],
    },
    "F10": {
        "name": "Secrets-Disclosed-Outsiders", "side": "d",
        "verbatim": "Plaintiff disclosed its product information to outsiders.",
        "definition": "Plaintiff disclosed the information to outsiders (third parties other than defendant), weakening secrecy.",
        "requirements": [
            "Plaintiff is described as revealing the information to third parties who are not the defendant.",
        ],
        "extra_bans": [
            "The disclosures must carry NO confidentiality restriction (with restrictions it is F12).",
            "Not a bilateral negotiation with defendant (F1) and not a public forum (F27); ordinary disclosure to specific outsiders.",
            "Narrate ONLY the specific disclosure event, as a plain fact. Do NOT emphasise the absence of restrictions in any wording ('freely', 'openly', 'without conditions', 'no restrictions', 'unsecured') -- simply do not mention restrictions at all. Any absence-emphasis reads as F19 (no-security-measures).",
        ],
        "lexical_pool": [
            "shared the specifications with several unaffiliated distributors",
            "handed the process details to two contract manufacturers",
            "showed the design to a group of prospective customers",
            "circulated the data among outside consultants",
            "let visiting industry peers inspect the line",
            "provided the formulation to a supplier",
            "disclosed the method to a trade partner",
            "gave the drawings to outside vendors",
        ],
    },
    "F11": {
        "name": "Vertical-Knowledge", "side": "d",
        "verbatim": "Plaintiff's information is about customers and suppliers.",
        "definition": "The information concerns customers or suppliers, so it may be available independently from those third parties or directories.",
        "requirements": [
            "The information at issue is identified as customer/supplier identities or relationships (not a technical secret).",
        ],
        "extra_bans": [
            "Do NOT frame it as a formula/process/design; the point is that it is business-relationship knowledge.",
            "Do NOT assert that competitors, the trade, or the public know or could find this information (that is F20/F24) -- state only WHAT the information is, never who else knows it or where it could be found.",
        ],
        "lexical_pool": [
            "a compilation of the customers who buy each product line",
            "records identifying its specialty suppliers by region",
            "the roster of distributor accounts and contact persons",
            "spreadsheets of buyer identities and order histories",
            "the list of vendors it sources components from",
            "account records naming its wholesale purchasers",
            "a directory of its supplier relationships and terms",
            "files identifying which retailers carry the line",
        ],
    },
    "F12": {
        "name": "Outsider-Disclosures-Restricted", "side": "p",
        "verbatim": "Plaintiff's disclosures to outsiders were subject to confidentiality restrictions.",
        "definition": "Plaintiff's disclosures to outsiders were made subject to confidentiality restrictions, preserving secrecy.",
        "requirements": [
            "Plaintiff disclosed to third parties BUT under explicit confidentiality conditions.",
        ],
        "extra_bans": [
            "The restriction must attach to the OUTSIDER disclosure; do not describe the defendant's own NDA (F4).",
            "Do NOT describe internal security measures (F6).",
        ],
        "lexical_pool": [
            "each contractor signed a confidentiality undertaking before review",
            "disclosures to suppliers were conditioned on secrecy agreements",
            "outside labs received the data only under NDA",
            "prospective partners were bound by confidentiality before any showing",
            "vendors accessed the drawings subject to nondisclosure terms",
            "every third-party recipient acknowledged the material was confidential",
            "disclosure to consultants required signed secrecy commitments",
            "customers previewed the product under a written confidentiality rider",
        ],
    },
    "F13": {
        "name": "Non-Competition-Agreement", "side": "p",
        "verbatim": "Plaintiff and defendant entered into a non-competition agreement.",
        "definition": "Plaintiff and the defendant (or departing employee) entered into a non-competition agreement.",
        "requirements": [
            "A non-compete / covenant-not-to-compete between the parties is described.",
        ],
        "extra_bans": [
            "Distinguish from a confidentiality/NDA (F4): this restrains COMPETITION or employment, not disclosure.",
        ],
        "lexical_pool": [
            "a two-year covenant not to compete within the region",
            "the employment contract barred joining a competitor for eighteen months",
            "a non-compete clause restricting work in the same field",
            "signed an agreement not to enter the rival market",
            "the covenant prohibited soliciting the same customers",
            "a restraint on competing employment within fifty miles",
            "agreed not to work for a direct competitor for one year",
            "the contract's non-competition term covered the product category",
        ],
    },
    "F14": {
        "name": "Restricted-Materials-Used", "side": "p",
        "verbatim": "Defendant used materials that were subject to confidentiality restrictions.",
        "definition": "Defendant actually used materials that were subject to plaintiff's confidentiality restrictions.",
        "requirements": [
            "Defendant is described as USING materials that bore or were subject to confidentiality restrictions.",
        ],
        "extra_bans": [
            "Focus on USE of restricted materials by defendant; do not describe the employee bringing them (F7) or how they were taken.",
        ],
        "lexical_pool": [
            "incorporated the confidential drawings into its own product",
            "ran production using plaintiff's restricted process sheets",
            "built prototypes from the proprietary specifications it held under NDA",
            "applied the confidential test data in its development",
            "used the marked-confidential schematics on its assembly line",
            "relied on the restricted formulation to make its goods",
            "operated from the secrecy-bound engineering files",
            "deployed the confidential customer data in its sales effort",
        ],
    },
    "F15": {
        "name": "Unique-Product", "side": "p",
        "verbatim": "Plaintiff was the only manufacturer making the product.",
        "definition": "Plaintiff was the sole manufacturer of the product, indicating the information's value and secrecy.",
        "requirements": [
            "The text states plaintiff was the only maker of the product in the market.",
        ],
        "extra_bans": [
            "Do NOT say defendant's product is identical (F18); only that plaintiff was the unique manufacturer.",
        ],
        "lexical_pool": [
            "the only firm in the world producing this grade of material",
            "no other manufacturer offered a comparable product",
            "plaintiff alone had brought such a device to market",
            "the sole source for this specialized component",
            "unmatched by any competing product then available",
            "the market's only supplier of the formulation",
            "no rival had succeeded in making anything equivalent",
            "the exclusive producer of the process's output",
        ],
    },
    "F17": {
        "name": "Info-Independently-Generated", "side": "d",
        "verbatim": "Defendant developed its product by independent research.",
        "definition": "Defendant developed its product through its own independent research, not from plaintiff's information.",
        "requirements": [
            "Defendant is described as arriving at the information through its own independent development effort.",
        ],
        "extra_bans": [
            "Distinguish from F3 (employee was plaintiff's sole developer): here DEFENDANT independently develops, typically after the fact.",
            "Do NOT describe reverse-engineering plaintiff's product (F25).",
        ],
        "lexical_pool": [
            "arrived at the same process through its own multi-year research",
            "developed the design independently in its own laboratories",
            "reached the result via a separate, documented R&D program",
            "its engineers derived the method without reference to plaintiff",
            "built the product from its own prior patents and experiments",
            "independent testing led it to the identical solution",
            "the parallel development was recorded in its own lab notebooks",
            "created the formulation through unrelated internal work",
        ],
    },
    "F18": {
        "name": "Identical-Products", "side": "p",
        "verbatim": "Defendant's product was identical to plaintiff's.",
        "definition": "Defendant's product was identical to plaintiff's, suggesting copying rather than independent creation.",
        "requirements": [
            "The text states defendant's product is identical or a near-exact copy of plaintiff's.",
        ],
        "extra_bans": [
            "Do NOT describe HOW it was obtained (taking F7, bribery F2); only the identity of the products.",
            "Do NOT assert independent development (F17).",
        ],
        "lexical_pool": [
            "the two products were indistinguishable down to the tolerances",
            "an exact duplicate, including the same idiosyncratic dimensions",
            "identical formulation, matching even the trace additives",
            "the copy reproduced plaintiff's unique design errors",
            "a point-for-point match of the original specification",
            "the competing unit was a carbon copy of plaintiff's",
            "same code, comments and all, as plaintiff's software",
            "the product mirrored plaintiff's in every measurable respect",
        ],
    },
    "F19": {
        "name": "No-Security-Measures", "side": "d",
        "verbatim": "Plaintiff did not adopt any security measures.",
        "definition": "Plaintiff adopted no measures to protect the information, undercutting any claim of secrecy.",
        "requirements": [
            "The text affirmatively states plaintiff took NO steps to protect the information.",
        ],
        "extra_bans": [
            "STRICT: do not describe ANY protective measure, agreement, marking, or restriction (that would make it F6/F4/F21). The passage asserts the ABSENCE of protection.",
            "Assert the absence of safeguards WITHOUT narrating any actual disclosure to outsiders (that would be F10) and without any public dissemination (F27). Describe the internal state of affairs only.",
        ],
        "lexical_pool": [
            "kept the specifications on a shared drive with no access controls",
            "no markings, badges, or written policies governed the material",
            "the plant had no visitor-escort or sign-in practice of any kind",
            "took no steps to limit which employees could view the process",
            "the documents were stored in an unlocked common area",
            "never marked or catalogued the material as sensitive",
            "no exit procedure asked departing staff to return anything",
            "the company had no confidentiality training or policy at all",
        ],
    },
    "F20": {
        "name": "Info-Known-To-Competitors", "side": "d",
        "verbatim": "Plaintiff's information was known to competitors.",
        "definition": "The information was already known to competitors in the trade, so it was not a secret.",
        "requirements": [
            "The text states the information was already known to competitors or generally in the industry.",
        ],
        "extra_bans": [
            "Distinguish from F24 (obtainable from public sources): here it is ALREADY KNOWN to competitors, not merely ascertainable.",
        ],
        "lexical_pool": [
            "every competitor in the sector already used the same approach",
            "the technique was common knowledge among rival engineers",
            "other manufacturers had long employed the identical process",
            "the parameters were well known throughout the industry",
            "competitors had independently arrived at the method years earlier",
            "the design was standard practice among peer firms",
            "the formulation was familiar to anyone in the trade",
            "rivals openly discussed the same specifications at conferences",
        ],
    },
    "F22": {
        "name": "Invasive-Techniques", "side": "p",
        "verbatim": "Defendant used invasive techniques to gain access to plaintiff's information.",
        "definition": "Defendant used invasive techniques (intrusion, surveillance, hacking) to gain access to the information.",
        "requirements": [
            "Defendant is described as using intrusive means: trespass, wiretap, hacking, aerial/photographic surveillance, planted devices.",
        ],
        "extra_bans": [
            "Distinguish from deception (F26, obtaining by false pretenses) and from bribery (F2): here the means are INTRUSIVE, not deceptive or inducing.",
        ],
        "lexical_pool": [
            "flew a low aircraft to photograph the unroofed plant under construction",
            "planted a recording device in the research wing",
            "breached the network and exfiltrated the design files",
            "trespassed onto the site to photograph the line at night",
            "intercepted the company's engineering communications",
            "used a hidden camera to capture the process settings",
            "hacked the credentials of a project engineer",
            "conducted covert surveillance of the loading dock and lab",
        ],
    },
    "F23": {
        "name": "Waiver-Of-Confidentiality", "side": "d",
        "verbatim": "Plaintiff entered into an agreement waiving confidentiality.",
        "definition": "Plaintiff entered into an agreement that waived confidentiality in the information.",
        "requirements": [
            "The text describes plaintiff signing/agreeing to something that expressly waived or released confidentiality.",
        ],
        "extra_bans": [
            "This is the OPPOSITE of an NDA (F4): plaintiff gives up secrecy by agreement. Do not describe a protective agreement.",
        ],
        "lexical_pool": [
            "signed a release permitting the licensee to publish the method",
            "the settlement expressly waived any confidentiality in the data",
            "agreed the specifications could be shared without restriction",
            "a contract clause released the process from secrecy obligations",
            "consented in writing to public use of the design",
            "the joint-venture terms disclaimed confidentiality in the results",
            "waived secrecy of the formulation under the supply agreement",
            "the license permitted unrestricted redisclosure by the partner",
        ],
    },
    "F24": {
        "name": "Info-Obtainable-Elsewhere", "side": "d",
        "verbatim": "The information could be obtained from publicly available sources.",
        "definition": "The information could be obtained from publicly available sources other than plaintiff.",
        "requirements": [
            "The text states the information is available from public sources: publications, patents, catalogs, standards.",
        ],
        "extra_bans": [
            "Distinguish from F16 (learnable by reverse-engineering the product) and F20 (already known to competitors): here it is ASCERTAINABLE FROM PUBLIC SOURCES.",
            "State only that the information CAN be found in public sources. Do NOT say competitors, rivals, or the trade already know or use it (that is F20), and do not mention plaintiff publishing it (F27).",
        ],
        "lexical_pool": [
            "the same parameters appear in an expired public patent",
            "published handbooks give the identical formulation",
            "the method is described in a widely available textbook",
            "public standards bodies specify the very tolerances at issue",
            "any library's trade literature sets out the process",
            "the design is documented in openly available datasheets",
            "government filings disclose the same specifications",
            "the information is compiled in a public industry catalog",
        ],
    },
    "F25": {
        "name": "Info-Reverse-Engineered", "side": "d",
        "verbatim": "Defendant discovered plaintiff's information through reverse engineering.",
        "definition": "Defendant actually discovered the information by reverse-engineering plaintiff's publicly sold product.",
        "requirements": [
            "Defendant is described as HAVING reverse-engineered a lawfully obtained product to derive the information.",
        ],
        "extra_bans": [
            "Distinguish from F16 (the product COULD be reverse-engineered, an objective property): here defendant ACTUALLY DID it.",
        ],
        "lexical_pool": [
            "bought the unit on the open market and disassembled it",
            "its engineers decompiled the shipped binary to recover the logic",
            "reverse-engineered the retail product to derive the tolerances",
            "chemically analyzed a purchased sample to obtain the formulation",
            "tore down the device and measured every component",
            "recovered the process by assaying the finished goods it acquired",
            "traced the circuit by inspecting a lawfully bought board",
            "reconstructed the design from a product it purchased at retail",
        ],
    },
    "F26": {
        "name": "Deception", "side": "p",
        "verbatim": "Defendant obtained plaintiff's information through deception.",
        "definition": "Defendant obtained the information through deception or false pretenses.",
        "requirements": [
            "Defendant is described as obtaining access by deceit: posing as someone else, faking a deal, misrepresenting purpose.",
        ],
        "extra_bans": [
            "Distinguish from invasion (F22, intrusive means) and bribery (F2, inducing an employee): here the means is FALSE PRETENSES.",
            "Do NOT stage the deception as business negotiations, licensing talks, a demo to a prospective buyer, or a partnership discussion -- plaintiff disclosing during negotiations is F1. The false pretense must be a non-negotiation role (researcher, journalist, surveyor, standards body, distributor inquiry).",
            "The deception must NOT involve entering premises, gaining system access, or passing any access control (that reads as F22 intrusion and implies F6 measures). No words like restricted, access, warehouse entry, badges. The trick obtains INFORMATION through correspondence or conversation only.",
        ],
        "lexical_pool": [
            "sent an agent under a false name to request the drawings by mail",
            "posed as a graduate researcher to obtain the test protocol",
            "submitted a sham customer questionnaire to elicit the specifications",
            "invented a fictitious trade publication to interview the engineers",
            "used a fabricated purchase order to obtain product documentation",
            "pretended to be a prospective distributor requesting technical sheets",
            "claimed a false standards-body role to request the process data",
            "staged a bogus market survey to collect the pricing model",
        ],
    },
}

ALL_FACTORS = {**FACTORS, **FACTORS_EXT}

# --- Registered entailment lattice ------------------------------------------
# Discovered empirically at 27-factor scale (2026-07-19): three model families
# independently annotated these as co-present because they are LOGICAL
# entailments of the CATO definitions, not generation leakage. You cannot write
# "defendant reverse-engineered the product" without it being true that the
# product was reverse-engineerable. The registered F4=>F21 case in the
# pre-registration turns out to be one instance of this wider lattice, which the
# 8-factor subset hid. Retention rule: an entailed factor co-occurring with its
# entailer is ALLOWED (not counted as contamination); probes additionally
# exclude an entailer's positives from the entailed factor's negative pool.
ENTAILMENTS = {
    "F4": ["F21"],   # an NDA gives the defendant notice of confidentiality
    "F11": ["F24"],  # customer/supplier info is obtainable from directories
    "F12": ["F6"],   # restricting outsider disclosure IS a protective measure
    "F14": ["F21", "F6"],  # restricted materials imply notice + measures
    "F20": ["F24"],  # known to competitors implies obtainable elsewhere
    "F25": ["F16"],  # having reverse-engineered implies reverse-engineerable
    "F27": ["F10"],  # public disclosure is a disclosure to outsiders
}
for _fid, _ent in ENTAILMENTS.items():
    if _fid in ALL_FACTORS:
        ALL_FACTORS[_fid]["entails"] = list(_ent)


def entailed_by(fid, factor_set=None):
    """Factors that fid logically entails (allowed to co-occur with fid)."""
    fs = factor_set if factor_set is not None else ACTIVE
    spec = fs.get(fid, {})
    out = set(spec.get("entails", []))
    if spec.get("secondary"):          # legacy single-value form
        out.add(spec["secondary"])
    return {x for x in out if x in fs}


def entailers_of(fid, factor_set=None):
    """Factors whose positives are not valid negatives for fid."""
    fs = factor_set if factor_set is not None else ACTIVE
    return {x for x in fs if fid in entailed_by(x, fs)}

# 27-factor clusters (opposed/co-occurring groups for hard-negative pairing)
CLUSTERS_27 = {
    "secrecy_maintenance": ["F4", "F5", "F6", "F12", "F13", "F19", "F21", "F23"],
    "improper_acquisition": ["F2", "F7", "F14", "F22", "F26"],
    "plaintiff_self_disclosure": ["F1", "F10", "F27"],
    "info_availability": ["F11", "F16", "F17", "F20", "F24", "F25"],
    "product_value_identity": ["F3", "F8", "F15", "F18"],
}
# opposed pairs that make the sharpest hard negatives
OPPOSED_PAIRS_27 = [("F6", "F19"), ("F16", "F25"), ("F10", "F12"),
                    ("F4", "F23"), ("F3", "F17"), ("F1", "F27")]


def factor_list_text(factor_set=None):
    fs = factor_set if factor_set is not None else ACTIVE
    return "\n".join(f"- {fid} {spec['name']} ({spec['side']}): {spec['definition']}"
                     for fid, spec in fs.items())


# --- active factor set -------------------------------------------------------
# Scripts call use_set("8") for the pilot or use_set("27") for the complete
# CATO catalog used in the paper. Modules that read factors.ACTIVE /
# factors.factor_list_text() at call time pick this up automatically.
ACTIVE = ALL_FACTORS
ACTIVE_NAME = "27"


def use_set(name):
    """Select the active factor set: '8' (frozen 8-factor) or '27' (full CATO)."""
    global ACTIVE, ACTIVE_NAME, FACTOR_LIST_TEXT
    if str(name) in ("27", "all", "full"):
        ACTIVE, ACTIVE_NAME = ALL_FACTORS, "27"
    else:
        ACTIVE, ACTIVE_NAME = FACTORS, "8"
    FACTOR_LIST_TEXT = factor_list_text(ACTIVE)
    return ACTIVE


def add_set_arg(ap):
    """Register the shared --factor-set flag on an argparse parser."""
    ap.add_argument("--factor-set", default="27", choices=["8", "27"],
                    help="which CATO factor set the prompts and labels cover")


FACTOR_LIST_TEXT = factor_list_text(ALL_FACTORS)
