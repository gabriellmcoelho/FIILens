const API_BASE_URL = import.meta.env.PROD 
  ? 'https://fiilens.onrender.com/api/v1'
  : 'http://localhost:3333/api/v1'

export { API_BASE_URL }
