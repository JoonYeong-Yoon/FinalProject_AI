import SwiftUI

@main
struct HealthkitTestApp: App {

    @State private var isLoggedIn: Bool =
        !(UserDefaults.standard.string(forKey: "userEmail") ?? "").isEmpty

    var body: some Scene {
        WindowGroup {
            if isLoggedIn {
                ContentView()
            } else {
                EmailLoginView(isLoggedIn: $isLoggedIn)
            }
        }
    }
}

