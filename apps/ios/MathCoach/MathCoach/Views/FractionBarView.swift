//
//  FractionBarView.swift
//  MathCoach
//
//  Visual bar showing a fraction by shading numerator out of denominator cells.
//  Extracted from Item.parameters when present.
//

import SwiftUI

struct FractionBarView: View {
    let numerator: Int
    let denominator: Int
    var height: CGFloat = 48
    var shadedColor: Color = .blue
    var emptyColor: Color = Color.gray.opacity(0.15)

    private var clampedNumerator: Int {
        max(0, min(numerator, denominator))
    }

    var body: some View {
        VStack(spacing: 8) {
            GeometryReader { geo in
                HStack(spacing: 2) {
                    ForEach(0..<denominator, id: \.self) { i in
                        Rectangle()
                            .fill(i < clampedNumerator ? shadedColor : emptyColor)
                            .overlay(
                                Rectangle().stroke(Color.gray.opacity(0.4), lineWidth: 1)
                            )
                    }
                }
                .frame(width: geo.size.width, height: height)
            }
            .frame(height: height)

            Text("\(clampedNumerator)/\(denominator)")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }

    static func extract(from parameters: [String: AnyCodable]) -> FractionBarView? {
        let numKeys = ["num", "numerator", "n", "shaded"]
        let denKeys = ["denom", "denominator", "d", "total"]
        var num: Int?
        var den: Int?
        for k in numKeys where num == nil {
            if let v = parameters[k]?.value as? Int { num = v }
            else if let v = parameters[k]?.value as? Double { num = Int(v) }
        }
        for k in denKeys where den == nil {
            if let v = parameters[k]?.value as? Int { den = v }
            else if let v = parameters[k]?.value as? Double { den = Int(v) }
        }
        guard let n = num, let d = den, d > 0, d <= 24 else { return nil }
        return FractionBarView(numerator: n, denominator: d)
    }
}

#Preview {
    VStack(spacing: 24) {
        FractionBarView(numerator: 3, denominator: 8)
        FractionBarView(numerator: 5, denominator: 6, shadedColor: .purple)
        FractionBarView(numerator: 1, denominator: 4, shadedColor: .green)
    }
    .padding()
}
