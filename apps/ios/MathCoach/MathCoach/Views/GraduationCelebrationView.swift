//
//  GraduationCelebrationView.swift
//  MathCoach
//
//  Confetti + headline shown when student graduates to a new stage.
//

import SwiftUI

struct GraduationCelebrationView: View {
    let stageLabel: String
    var onDismiss: () -> Void

    @State private var startedAt: Date = .now
    @State private var sparkleOpacity: Double = 0

    fileprivate static let confettiColors: [Color] = [
        .red, .orange, .yellow, .green, .blue, .purple, .pink
    ]

    var body: some View {
        ZStack {
            Color.black.opacity(0.55).ignoresSafeArea()
                .onTapGesture { onDismiss() }

            ConfettiLayer(seed: startedAt.timeIntervalSince1970)
                .allowsHitTesting(false)

            VStack(spacing: 18) {
                Text("🎉")
                    .font(.system(size: 96))
                    .opacity(sparkleOpacity)
                    .scaleEffect(sparkleOpacity == 1 ? 1.0 : 0.6)
                    .animation(.spring(response: 0.5, dampingFraction: 0.55), value: sparkleOpacity)

                Text("升级啦！")
                    .font(.system(size: 44, weight: .heavy))
                    .foregroundColor(.white)

                Text(stageLabel)
                    .font(.title2.bold())
                    .foregroundColor(.yellow)
                    .padding(.horizontal, 24)
                    .padding(.vertical, 10)
                    .background(Capsule().fill(Color.white.opacity(0.12)))

                Text("点屏幕继续")
                    .font(.footnote)
                    .foregroundColor(.white.opacity(0.7))
                    .padding(.top, 12)
            }
            .padding(36)
            .background(
                RoundedRectangle(cornerRadius: 32)
                    .fill(LinearGradient(
                        colors: [Color.indigo, Color.purple, Color.pink],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ))
                    .shadow(color: .black.opacity(0.4), radius: 30, y: 16)
            )
            .padding(.horizontal, 32)
        }
        .onAppear {
            sparkleOpacity = 1
            DispatchQueue.main.asyncAfter(deadline: .now() + 6.0) {
                onDismiss()
            }
        }
    }
}

private struct ConfettiLayer: View {
    let seed: Double

    var body: some View {
        GeometryReader { geo in
            ZStack {
                ForEach(0..<60, id: \.self) { i in
                    ConfettiPiece(index: i, seed: seed, canvas: geo.size)
                }
            }
        }
    }
}

private struct ConfettiPiece: View {
    let index: Int
    let seed: Double
    let canvas: CGSize

    @State private var animate = false

    private var rng: SeededRandom { SeededRandom(seed: UInt64(bitPattern: Int64(seed)) &+ UInt64(index)) }

    var body: some View {
        let r = rng
        let startX = r.nextCGFloat(in: 0...canvas.width)
        let endX = startX + r.nextCGFloat(in: -120...120)
        let delay = r.nextDouble(in: 0...1.2)
        let duration = r.nextDouble(in: 2.0...3.6)
        let color = GraduationCelebrationView.confettiColors[r.nextInt(modulo: GraduationCelebrationView.confettiColors.count)]
        let size = r.nextCGFloat(in: 8...16)
        let rot = r.nextDouble(in: 0...720)

        return Rectangle()
            .fill(color)
            .frame(width: size, height: size * 0.5)
            .rotationEffect(.degrees(animate ? rot : 0))
            .position(x: animate ? endX : startX, y: animate ? canvas.height + 40 : -40)
            .opacity(animate ? 0.0 : 1.0)
            .onAppear {
                withAnimation(.easeIn(duration: duration).delay(delay)) {
                    animate = true
                }
            }
    }
}

private struct SeededRandom {
    var state: UInt64
    init(seed: UInt64) { self.state = seed == 0 ? 0x9E3779B97F4A7C15 : seed }

    mutating func next() -> UInt64 {
        state &+= 0x9E3779B97F4A7C15
        var z = state
        z = (z ^ (z >> 30)) &* 0xBF58476D1CE4E5B9
        z = (z ^ (z >> 27)) &* 0x94D049BB133111EB
        return z ^ (z >> 31)
    }

    func nextInt(modulo m: Int) -> Int {
        var copy = self
        return Int(copy.next() % UInt64(m))
    }

    func nextDouble(in range: ClosedRange<Double>) -> Double {
        var copy = self
        let v = Double(copy.next() % 10000) / 10000.0
        return range.lowerBound + v * (range.upperBound - range.lowerBound)
    }

    func nextCGFloat(in range: ClosedRange<CGFloat>) -> CGFloat {
        return CGFloat(nextDouble(in: Double(range.lowerBound)...Double(range.upperBound)))
    }
}

#Preview {
    GraduationCelebrationView(stageLabel: "Year 4 Fractions & Decimals", onDismiss: {})
}
