
export interface AuthUser {
    id: string;
    name: string;
    email: string;
    role: 'USER' | 'ADMIN' | string;
  }
  
  export interface LoginRequest {
    email: string;
    password: string;
  }
  
  export interface LoginResponse {
    access_token: string;
    token_type: string;
    user: AuthUser;
  }
  