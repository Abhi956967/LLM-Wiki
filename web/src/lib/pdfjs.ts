import { pdfjs } from 'react-pdf'

export function ensurePdfWorker(): void {
  if (typeof window !== 'undefined') {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    if (typeof (window as any).Promise.withResolvers === 'undefined') {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).Promise.withResolvers = function () {
        let resolve: any, reject: any
        const promise = new Promise((res, rej) => {
          resolve = res
          reject = rej
        })
        return { promise, resolve, reject }
      }
    }
    if (pdfjs && pdfjs.GlobalWorkerOptions) {
      if (!pdfjs.GlobalWorkerOptions.workerSrc) {
        pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version || '4.8.69'}/build/pdf.worker.min.mjs`
      }
    }
  }
}

export { pdfjs }
