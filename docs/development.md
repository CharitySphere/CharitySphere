## Functional Requirements

#### 1. Authentication and Authorization

- [ ] Register an account (Roles: Donor, Institution, Volunteer)
- [ ] Show error messages on unsuccessful login
- [ ] Redirect to dashboard on successful login
- [ ] Redirect to login page on logout
- [ ] Register with Google/Facebook OAuth

#### 9. Profile and Settings

- [ ] View profile
- [ ] Update username and profile picture
- [ ] Donation History
- [ ] Delete account

## Module Architecture

```mermaid
flowchart TD
    app --> mod_auth{{Authentication}}
    mod_auth --> logi(Login) & regi(Registration)
    regi <--> logi --> dash(Dashboard)

    dash --> dona(🪙 Donate)
    dash --> voln(👤 Volunteer)
    dash --> inst(🏢 Institutions)
    dash --> anal[[Analytics]]
    dash --> prof(Profile)
    dash --> mod_emerg{{🗺️ Emergency Mode}}
    dash --> mod_ai{{✨ AI Chatbot}}

    prof --> dono(👤 Donors) & inst & voln

    inst --CRUD--> voln
    inst --CRUD--> mod_fund{{Fundraise}}
    inst --CRUD--> mod_task{{Tasks}} --> voln
    dono & inst & voln --> dona --> mod_fund
    mod_fund --> mod_pay{{Payments}}
```

