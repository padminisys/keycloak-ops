# Next.js Configuration Templates

## Environment Variables (.env.local)

```bash
# Keycloak Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-change-me

# Keycloak Provider
KEYCLOAK_ID=ppcs-web-app
KEYCLOAK_SECRET=  # Not needed for public client
KEYCLOAK_ISSUER=https://iam.padmini.systems/realms/padmini-systems

# API Configuration
API_BASE_URL=https://api.padmini.systems
```

## NextAuth Configuration (pages/api/auth/[...nextauth].js)

```javascript
import NextAuth from 'next-auth'
import KeycloakProvider from 'next-auth/providers/keycloak'

export default NextAuth({
  providers: [
    KeycloakProvider({
      clientId: process.env.KEYCLOAK_ID,
      clientSecret: process.env.KEYCLOAK_SECRET || '', // Empty for public client
      issuer: process.env.KEYCLOAK_ISSUER,
      authorization: {
        params: {
          scope: 'openid email profile mobile',
          response_type: 'code',
          prompt: 'login'
        }
      },
      checks: ['pkce'], // Enable PKCE for public client
      profile: (profile) => {
        return {
          id: profile.sub,
          name: profile.name,
          email: profile.email,
          image: profile.picture,
          username: profile.preferred_username,
          mobile: profile.mobile,
          firstName: profile.given_name,
          lastName: profile.family_name
        }
      }
    })
  ],
  session: {
    strategy: 'jwt',
    maxAge: 30 * 60, // 30 minutes
  },
  callbacks: {
    async jwt({ token, account, profile, user }) {
      // Persist the OAuth access_token to the token
      if (account) {
        token.accessToken = account.access_token
        token.refreshToken = account.refresh_token
        token.expiresAt = account.expires_at
        token.mobile = profile?.mobile
        token.username = profile?.preferred_username
      }
      
      // Return previous token if the access token has not expired yet
      if (Date.now() < token.expiresAt * 1000) {
        return token
      }
      
      // Access token has expired, try to refresh it
      return await refreshAccessToken(token)
    },
    async session({ session, token }) {
      // Send properties to the client
      session.accessToken = token.accessToken
      session.error = token.error
      session.user.id = token.sub
      session.user.mobile = token.mobile
      session.user.username = token.username
      return session
    }
  },
  pages: {
    signIn: '/auth/signin',
    signUp: '/auth/signup',
    error: '/auth/error',
  },
  debug: process.env.NODE_ENV === 'development',
})

async function refreshAccessToken(token) {
  try {
    const url = `${process.env.KEYCLOAK_ISSUER}/protocol/openid-connect/token`
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        client_id: process.env.KEYCLOAK_ID,
        grant_type: 'refresh_token',
        refresh_token: token.refreshToken,
      }),
      method: 'POST',
    })

    const tokens = await response.json()

    if (!response.ok) throw tokens

    return {
      ...token,
      accessToken: tokens.access_token,
      expiresAt: Math.floor(Date.now() / 1000 + tokens.expires_in),
      refreshToken: tokens.refresh_token ?? token.refreshToken,
    }
  } catch (error) {
    console.error('Error refreshing access token', error)
    return {
      ...token,
      error: 'RefreshAccessTokenError',
    }
  }
}
```

## API Client (lib/api.js)

```javascript
import { getSession } from 'next-auth/react'

class ApiClient {
  constructor() {
    this.baseURL = process.env.API_BASE_URL || 'https://api.padmini.systems'
  }

  async getAuthHeaders() {
    const session = await getSession()
    if (!session?.accessToken) {
      throw new Error('No access token available')
    }
    
    return {
      'Authorization': `Bearer ${session.accessToken}`,
      'Content-Type': 'application/json',
    }
  }

  async post(endpoint, data) {
    const headers = await this.getAuthHeaders()
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }

    return response.json()
  }

  async get(endpoint) {
    const headers = await this.getAuthHeaders()
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'GET',
      headers,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }

    return response.json()
  }

  // User onboarding API call
  async completeOnboarding(userProfile, additionalData) {
    return this.post('/api/user/onboard', {
      userProfile,
      additionalData,
      timestamp: new Date().toISOString()
    })
  }

  // Get user profile
  async getUserProfile() {
    return this.get('/api/user/profile')
  }
}

export default new ApiClient()
```

## User Profile Component (components/UserProfile.jsx)

```jsx
import { useSession } from 'next-auth/react'
import { useState, useEffect } from 'react'
import ApiClient from '../lib/api'

export default function UserProfile() {
  const { data: session, status } = useSession()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (session?.user) {
      fetchProfile()
    }
  }, [session])

  const fetchProfile = async () => {
    try {
      const profileData = await ApiClient.getUserProfile()
      setProfile(profileData)
    } catch (error) {
      console.error('Failed to fetch profile:', error)
    } finally {
      setLoading(false)
    }
  }

  if (status === 'loading' || loading) {
    return <div>Loading...</div>
  }

  if (!session) {
    return <div>Please sign in</div>
  }

  return (
    <div className="user-profile">
      <h2>User Profile</h2>
      <div className="profile-info">
        <p><strong>Name:</strong> {session.user.name}</p>
        <p><strong>Email:</strong> {session.user.email}</p>
        <p><strong>Username:</strong> {session.user.username}</p>
        <p><strong>Mobile:</strong> {session.user.mobile}</p>
        <p><strong>User ID:</strong> {session.user.id}</p>
      </div>
      
      {profile && (
        <div className="business-profile">
          <h3>Business Profile</h3>
          <pre>{JSON.stringify(profile, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
```

## Onboarding Component (components/Onboarding.jsx)

```jsx
import { useState } from 'react'
import { useSession } from 'next-auth/react'
import ApiClient from '../lib/api'

export default function Onboarding() {
  const { data: session } = useSession()
  const [formData, setFormData] = useState({
    businessType: '',
    companyName: '',
    address: '',
    additionalInfo: ''
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Prepare user profile from Keycloak token
      const userProfile = {
        userId: session.user.id,
        username: session.user.username,
        email: session.user.email,
        mobile: session.user.mobile,
        name: session.user.name,
        firstName: session.user.firstName,
        lastName: session.user.lastName
      }

      // Call ASM API for complete onboarding
      await ApiClient.completeOnboarding(userProfile, formData)
      
      alert('Onboarding completed successfully!')
    } catch (error) {
      console.error('Onboarding failed:', error)
      alert('Onboarding failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="onboarding-form">
      <h2>Complete Your Onboarding</h2>
      
      <div className="form-group">
        <label>Business Type:</label>
        <select 
          value={formData.businessType}
          onChange={(e) => setFormData({...formData, businessType: e.target.value})}
          required
        >
          <option value="">Select Business Type</option>
          <option value="individual">Individual</option>
          <option value="small-business">Small Business</option>
          <option value="enterprise">Enterprise</option>
        </select>
      </div>

      <div className="form-group">
        <label>Company Name:</label>
        <input
          type="text"
          value={formData.companyName}
          onChange={(e) => setFormData({...formData, companyName: e.target.value})}
          required
        />
      </div>

      <div className="form-group">
        <label>Address:</label>
        <textarea
          value={formData.address}
          onChange={(e) => setFormData({...formData, address: e.target.value})}
          required
        />
      </div>

      <div className="form-group">
        <label>Additional Information:</label>
        <textarea
          value={formData.additionalInfo}
          onChange={(e) => setFormData({...formData, additionalInfo: e.target.value})}
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Processing...' : 'Complete Onboarding'}
      </button>
    </form>
  )
}
```

## Package.json Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "next-auth": "^4.24.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
```
