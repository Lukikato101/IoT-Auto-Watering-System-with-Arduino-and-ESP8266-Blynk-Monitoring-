function StatusCard({
    title,
    value,
    color
}) {
    return (
        <div className="
            bg-gray-900
            p-6
            rounded-2xl
            w-full
        ">
            <h2 className="
                text-gray-400
                mb-3
            ">
                {title}
            </h2>

            <p className="
                text-5xl
                font-bold
                ${color}
            ">
                {value}
            </p>
        </div>
    )
}

export default StatusCard