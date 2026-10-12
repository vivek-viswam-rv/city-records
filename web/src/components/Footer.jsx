export default function Footer() {
  return (
    <footer className="mt-10 border-t border-slate-200 py-6 text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">
      <div className="mx-auto max-w-7xl px-4">
        <p>
          Source: NYC Open Data, City Record Online (dg92-zbpx). Pipeline: Dagster on GKE · Enrichment: gpt-oss on Bedrock · Storage: Postgres + S3.
        </p>
        <p className="mt-1">
          <a className="underline" href="https://github.com/vivek-viswam-rv/city-records" target="_blank" rel="noreferrer">GitHub</a>
        </p>
      </div>
    </footer>
  )
}
