from __future__ import annotations


class VisionProcessorService:
    def describe_images(self, images: list[bytes]) -> list[str]:
        descriptions: list[str] = []

        for index, image in enumerate(images, start=1):
            descriptions.append(
                "Screenshot "
                f"{index} appears to represent a UI state. "
                f"Binary size: {len(image)} bytes."
            )

        return descriptions
