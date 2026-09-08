export interface TeamMember {
    name: string;
    /** Papel no projeto — edite aqui para diferenciar cada pessoa. */
    designation: string;
    /** Opcional: caminho da foto em public/ (ex.: "/time/felipe.jpg").
     *  Sem foto, o card mostra as iniciais sobre a cor de destaque. */
    imageSrc?: string;
    color: string;
    /** Uma linha sobre o que a pessoa fez no projeto. */
    bio?: string;
    /** Perfis — troque os "#" pelas URLs reais. */
    instagram?: string;
    linkedin?: string;
}

const initials = (name: string) =>
    name
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0])
        .join("")
        .toUpperCase();

export const TEAM: TeamMember[] = [
    { name: "Felipe Neves", designation: "Desenvolvimento", color: "#818cf8", instagram: "#", linkedin: "#" },
    { name: "Henrique Diniz", designation: "Desenvolvimento", color: "#a78bfa", instagram: "#", linkedin: "#" },
    { name: "Wendel Feitosa", designation: "Desenvolvimento", color: "#38bdf8", instagram: "#", linkedin: "#" },
    { name: "Pedro Uchoa", designation: "Desenvolvimento", color: "#34d399", instagram: "#", linkedin: "#" },
    { name: "Leonardo Ramos", designation: "Desenvolvimento", color: "#fbbf24", instagram: "#", linkedin: "#" },
    { name: "Jaime Almeida", designation: "Desenvolvimento", color: "#f472b6", instagram: "#", linkedin: "#" },
];

export const teamInitials = initials;
