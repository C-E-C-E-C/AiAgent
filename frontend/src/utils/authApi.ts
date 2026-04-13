export async function validateBackendLogin(token: string) {
  try {
    const response = await fetch('http://localhost:8080/api/islogin', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    return response.ok;
  } catch {
    return false;
  }
}