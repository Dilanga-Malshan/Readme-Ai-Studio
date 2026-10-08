import { bootstrapApplication } from '@angular/platform-browser';
import { provideRouter } from '@angular/router';
import { AppComponent } from './app/app.component';
import { LandingComponent } from './app/landing.component';
import { ShareComponent } from './app/share.component';
import { StudioComponent } from './app/studio.component';
bootstrapApplication(AppComponent,{providers:[provideRouter([{path:'',component:LandingComponent},{path:'studio',component:StudioComponent},{path:'share/:token',component:ShareComponent},{path:'**',redirectTo:''}])]}).catch(console.error);
