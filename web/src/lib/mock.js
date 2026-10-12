// Mock data + in-memory implementation of the API contract (VITE_USE_MOCK=1).

// [agency, category, title, description, amount, vendor, whatIsBought, productCategory, isSoftware, isRenewal, confidence, keywords]
const SEEDS = [
  ['Police Department', 'Services (other than human services)', 'Body-Worn Camera Cloud Evidence Storage', 'Annual subscription for cloud storage and management of body-worn camera video evidence for uniformed members of service. Includes retention policy tooling and audit logs.', 18500000, 'Axon Enterprise, Inc.', 'Cloud video evidence storage subscription', 'Cloud / SaaS', true, true, 0.93, ['body camera', 'evidence', 'cloud storage']],
  ['Police Department', 'Goods', 'Patrol Vehicle Upfitting Equipment', 'Purchase of light bars, sirens and partition cages for new marked patrol vehicles. Delivery to the Fleet Services Division in Queens.', 2400000, 'Whelen Engineering Company', 'Emergency vehicle equipment', 'Vehicle Equipment', false, false, 0.88, ['patrol', 'light bar', 'vehicles']],
  ['Police Department', 'Services (other than human services)', 'Forensic DNA Analysis Software Licenses', 'Renewal of licenses for probabilistic genotyping software used by the Office of Chief Medical Examiner and NYPD crime lab.', 1250000, 'Cybergenetics Corp.', 'Forensic DNA analysis software licenses', 'Software Licenses', true, true, 0.91, ['forensics', 'DNA', 'licenses']],
  ['Police Department', 'Goods', 'Tactical Radio Replacement', 'Replacement of aging portable radios for the Emergency Service Unit with encrypted digital models.', 6800000, 'Motorola Solutions, Inc.', 'Encrypted portable radios', 'Communications Equipment', false, false, 0.84, ['radios', 'ESU', 'encryption']],
  ['Department of Education', 'Goods', 'Chromebook Devices for Grades 3-8', 'Procurement of Chromebook laptops with charging carts to support the 1:1 device initiative in elementary and middle schools.', 42000000, 'CDW Government LLC', 'Student Chromebook laptops', 'Computing Hardware', false, false, 0.95, ['chromebook', 'students', 'devices']],
  ['Department of Education', 'Services (other than human services)', 'Student Information System Support', 'Maintenance and support for the student information system used by all public schools for attendance, grades and scheduling.', 27500000, 'Infosys Public Services', 'Student information system maintenance', 'Software Maintenance', true, true, 0.87, ['SIS', 'attendance', 'support']],
  ['Department of Education', 'Human Services / Client Services', 'After-School Literacy Tutoring', 'Provision of small-group literacy tutoring for K-5 students in Community School Districts 7 and 9.', 3200000, 'Reading Partners New York', 'After-school tutoring services', 'Education Services', false, false, 0.79, ['tutoring', 'literacy', 'after-school']],
  ['Department of Education', 'Construction/Construction Services', 'HVAC Replacement at P.S. 121', 'Replacement of boilers and ventilation systems including asbestos abatement and associated electrical work.', 9400000, 'Metropolitan Mechanical Contracting', 'School HVAC construction', 'Construction', false, false, 0.9, ['HVAC', 'boiler', 'school']],
  ['Department of Parks and Recreation', 'Construction/Construction Services', 'Reconstruction of Playground at Mullaly Park', 'Reconstruction of playground, spray shower and perimeter fencing, including new safety surfacing and accessible paths.', 5600000, 'Kavanagh Construction Corp.', 'Playground reconstruction', 'Construction', false, false, 0.92, ['playground', 'Bronx', 'ADA']],
  ['Department of Parks and Recreation', 'Services (other than human services)', 'Tree Pruning Services - Brooklyn', 'Contract for routine pruning and removal of street and park trees in Brooklyn Community Boards 1 through 8.', 1900000, 'Asplundh Tree Expert LLC', 'Tree pruning services', 'Landscaping', false, false, 0.86, ['trees', 'pruning', 'Brooklyn']],
  ['Department of Parks and Recreation', 'Goods', 'Electric Mowers and Groundskeeping Equipment', 'Purchase of battery-electric mowers and trimmers for borough forestry and horticulture units.', 780000, 'Stihl Northeast', 'Battery-powered grounds equipment', 'Grounds Equipment', false, false, 0.81, ['electric', 'mowers', 'equipment']],
  ['Department of Parks and Recreation', 'Services (other than human services)', 'Online Permit and Reservation Platform', 'Hosted software platform for athletic field and event permit applications, payments and reporting.', 2100000, 'Tyler Technologies, Inc.', 'Permit management SaaS', 'Cloud / SaaS', true, false, 0.9, ['permits', 'platform', 'reservations']],
  ['Human Resources Administration/Department of Social Services', 'Human Services / Client Services', 'Emergency Shelter Services for Families', 'Operation of 80 units of emergency shelter for families with children, including social services and security.', 31000000, 'Acacia Network Housing, Inc.', 'Family shelter operation', 'Social Services', false, true, 0.85, ['shelter', 'families', 'case management']],
  ['Human Resources Administration/Department of Social Services', 'Services (other than human services)', 'Benefits Eligibility Case Management System Enhancements', 'Development services to enhance the case management system used to determine SNAP and cash assistance eligibility.', 14200000, 'Deloitte Consulting LLP', 'Custom software development', 'Software Development', true, false, 0.89, ['SNAP', 'eligibility', 'development']],
  ['Human Resources Administration/Department of Social Services', 'Human Services / Client Services', 'Home Care Services for Adults', 'Provision of home care aides for elderly and disabled clients in Manhattan and the Bronx.', 22800000, 'Selfhelp Community Services', 'Home care aide services', 'Healthcare Services', false, true, 0.8, ['home care', 'seniors', 'aides']],
  ['Human Resources Administration/Department of Social Services', 'Goods', 'Printing of Benefit Notices', 'Printing and mailing of eligibility notices and recertification packets in multiple languages.', 480000, 'Pitney Bowes Presort Services', 'Printing and mailing services', 'Printing', false, true, 0.74, ['printing', 'mailing', 'notices']],
  ['Department of Citywide Administrative Services', 'Goods', 'Citywide Light-Duty Electric Vehicles', 'Requirements contract for purchase of electric sedans and SUVs for use by city agencies.', 48000000, 'Ford Motor Company', 'Electric passenger vehicles', 'Vehicles', false, false, 0.94, ['EV', 'fleet', 'requirements contract']],
  ['Department of Citywide Administrative Services', 'Services (other than human services)', 'Microsoft Enterprise Licensing Agreement', 'Citywide enterprise licensing for Microsoft productivity and security software through a reseller.', 36500000, 'SHI International Corp.', 'Microsoft enterprise software licenses', 'Software Licenses', true, true, 0.96, ['Microsoft', 'enterprise', 'licenses']],
  ['Department of Citywide Administrative Services', 'Goods', 'Office Furniture - Citywide', 'Requirements contract for desks, ergonomic chairs and storage for agency offices.', 4300000, 'Krueger International', 'Office furniture', 'Furniture', false, true, 0.77, ['furniture', 'office', 'ergonomic']],
  ['Department of Citywide Administrative Services', 'Services (other than human services)', 'Janitorial Services at 1 Centre Street', 'Daily janitorial and cleaning services for municipal building and public areas.', 620000, 'Skyline Building Services', 'Janitorial services', 'Facilities Services', false, true, 0.72, ['janitorial', 'cleaning', 'municipal building']],
]

const TYPES = ['Award', 'Solicitation', 'Intent to Award', 'Public Hearings']
const CONTACTS = [['Maria Gonzalez', 'm.gonzalez'], ['David Chen', 'd.chen'], ['Aisha Johnson', 'a.johnson'], ['Robert Klein', 'r.klein']]
const ADDR = ['350 5th Ave, New York, NY 10118', '1 Metrotech Center, Brooklyn, NY 11201', '255 Greenwich St, New York, NY 10007', '100 Corporate Dr, Albany, NY 12205']
const EMAIL_DOMAIN = { 'Police Department': 'nypd.org', 'Department of Education': 'schools.nyc.gov', 'Department of Parks and Recreation': 'parks.nyc.gov', 'Human Resources Administration/Department of Social Services': 'dss.nyc.gov', 'Department of Citywide Administrative Services': 'dcas.nyc.gov' }

const vendorId = (name) => 'V' + String(Math.abs([...name].reduce((h, c) => (h * 31 + c.charCodeAt(0)) | 0, 7)) % 100000).padStart(5, '0')
const iso = (offsetDays) => new Date(Date.UTC(2026, 9, 10) - offsetDays * 86400000).toISOString().slice(0, 10)

function build() {
  const out = []
  SEEDS.forEach((s, i) => {
    const [agency, category, title, description, amount, vendorName, what, pcat, soft, renew, conf, kw] = s
    // Each seed yields two notices at different lifecycle stages.
    const variants = [
      [TYPES[(i + 1) % 3], i * 3 + 2],
      [TYPES[i % 7 === 3 ? 3 : (i + 2) % 3], i * 3 + 30],
    ]
    variants.forEach(([type, ago], v) => {
      const hearing = type === 'Public Hearings'
      const hasVendor = type === 'Award' || type === 'Intent to Award'
      const id = String(20260900000 + i * 10 + v * 3 + 1)
      const c = CONTACTS[(i + v) % CONTACTS.length]
      const noConf = (i + v) % 13 === 12
      out.push({
        request_id: id,
        published_on: iso(ago),
        end_date: type === 'Solicitation' ? iso(ago - 21) : null,
        section: hearing ? 'Public Hearings and Meetings' : 'Procurement',
        notice_type: type,
        agency,
        category: hearing ? 'Public Hearing' : category,
        title: hearing ? `Public Hearing: ${title}` : title,
        description: hearing ? `Public hearing to receive comment on the proposed contract for ${title.toLowerCase()}. Written comments are also accepted.` : description,
        selection_method: hearing ? null : v ? 'Competitive Sealed Bid' : 'Request for Proposals',
        pin: `${['056', '040', '846', '069', '857'][i % 5]}2026${String(i * 7 + 100 + v).padStart(4, '0')}`,
        contact_name: c[0],
        contact_email: `${c[1]}@${EMAIL_DOMAIN[agency]}`,
        contract_amount: hasVendor ? Math.round(amount * (v ? 0.8 : 1)) : null,
        vendor_name_raw: hasVendor ? vendorName.toUpperCase() : null,
        vendor: hasVendor ? { id: vendorId(vendorName), name: vendorName } : null,
        event_date: hearing ? iso(ago - 14) : null,
        enrichment: noConf ? null : {
          what_is_bought: what,
          product_category: pcat,
          is_software: soft,
          is_renewal: renew,
          summary: `${agency.split('/')[0]} ${hearing ? 'is holding a hearing on' : type === 'Solicitation' ? 'is seeking bids for' : 'is contracting for'} ${what.toLowerCase()}${hasVendor ? ` with ${vendorName}` : ''}. ${renew ? 'This appears to continue an existing arrangement.' : 'This appears to be a new purchase.'}`,
          keywords: kw,
          confidence: Math.max(0.3, +(conf - v * 0.12 - (i % 4 === 3 ? 0.2 : 0)).toFixed(2)),
          model: 'openai.gpt-oss-120b',
          prompt_version: 'v3',
          enriched_at: `${iso(ago - 1)}T06:15:00Z`,
        },
        _amount: amount,
      })
    })
  })
  return out.sort((a, b) => b.published_on.localeCompare(a.published_on))
}

const NOTICES = build()
const delay = (v) => new Promise((r) => setTimeout(() => r(v), 150))
const strip = (n) => { const { _amount, ...rest } = n; void _amount; return rest }

function filterNotices(p = {}) {
  const q = (p.q || '').toLowerCase()
  return NOTICES.filter((n) => {
    if (q && !`${n.title} ${n.description} ${n.vendor?.name || ''} ${n.enrichment?.keywords?.join(' ') || ''}`.toLowerCase().includes(q)) return false
    if (p.agency && n.agency !== p.agency) return false
    if (p.notice_type && n.notice_type !== p.notice_type) return false
    if (p.category && n.category !== p.category) return false
    if (p.product_category && n.enrichment?.product_category !== p.product_category) return false
    if (p.is_software && !n.enrichment?.is_software) return false
    if (p.min_amount && !((n.contract_amount ?? 0) >= Number(p.min_amount))) return false
    if (p.from && n.published_on < p.from) return false
    if (p.to && n.published_on > p.to) return false
    return true
  })
}

function weekOf(d) {
  const dt = new Date(d + 'T00:00:00Z')
  dt.setUTCDate(dt.getUTCDate() - ((dt.getUTCDay() + 6) % 7))
  return dt.toISOString().slice(0, 10)
}

export const mockApi = {
  notices(p = {}) {
    const all = filterNotices(p)
    const limit = Number(p.limit) || 25
    const offset = Number(p.offset) || 0
    return delay({ items: all.slice(offset, offset + limit).map(strip), total: all.length, has_more: offset + limit < all.length })
  },
  notice(id) {
    const n = NOTICES.find((x) => x.request_id === id)
    return n ? delay(strip(n)) : Promise.reject(new Error('Notice not found'))
  },
  vendor(id) {
    const ns = NOTICES.filter((n) => n.vendor?.id === id)
    if (!ns.length) return Promise.reject(new Error('Vendor not found'))
    const raw = ns[0].vendor_name_raw
    return delay({ id, name: ns[0].vendor.name, address: ADDR[Number(id.slice(1)) % ADDR.length], first_seen: ns[ns.length - 1].published_on, notices: ns.map(strip), raw })
  },
  stats(p = {}) {
    const ns = filterNotices(p)
    const awards = ns.filter((n) => n.notice_type === 'Award')
    const wk = {}
    const ag = {}
    const pc = {}
    ns.forEach((n) => {
      const k = `${weekOf(n.published_on)}|${n.notice_type}`
      wk[k] = wk[k] || { week: weekOf(n.published_on), notice_type: n.notice_type, usd: 0, count: 0 }
      wk[k].usd += n.contract_amount || 0
      wk[k].count += 1
      ag[n.agency] = ag[n.agency] || { agency: n.agency, count: 0, usd: 0 }
      ag[n.agency].count += 1
      ag[n.agency].usd += n.contract_amount || 0
      const c = n.enrichment?.product_category
      if (c) { pc[c] = pc[c] || { product_category: c, count: 0 }; pc[c].count += 1 }
    })
    return delay({
      notices: ns.length,
      open_solicitations: ns.filter((n) => n.notice_type === 'Solicitation').length,
      awarded_usd: awards.reduce((s, n) => s + n.contract_amount, 0),
      vendors: new Set(ns.filter((n) => n.vendor).map((n) => n.vendor.id)).size,
      by_week: Object.values(wk).sort((a, b) => a.week.localeCompare(b.week)),
      by_agency: Object.values(ag).sort((a, b) => b.count - a.count),
      by_product_category: Object.values(pc).sort((a, b) => b.count - a.count),
    })
  },
  filters() {
    const u = (f) => [...new Set(NOTICES.map(f).filter(Boolean))].sort()
    return delay({ agencies: u((n) => n.agency), notice_types: TYPES, categories: u((n) => n.category), product_categories: u((n) => n.enrichment?.product_category) })
  },
}
