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
    { name: "Felipe Neves", imageSrc: "/felipe.jpg", designation: "Desenvolvimento", color: "#818cf8", instagram: "https://www.instagram.com/ntsfelipe/", linkedin: "https://www.linkedin.com/in/ntsfelipe/" },
    { name: "Henrique Diniz", imageSrc: "/henrique.jpeg", designation: "Desenvolvimento", color: "#a78bfa", instagram: "https://www.instagram.com/1henriquediniz/", linkedin: "https://www.linkedin.com/in/henrique-rodrigues-diniz/" },
    { name: "Wendel Feitosa", imageSrc: "/wendel.jpeg", designation: "Desenvolvimento", color: "#38bdf8", instagram: "https://www.instagram.com/wendelhf_/", linkedin: "https://www.linkedin.com/in/wendel-feitosa-975bb1346/" },
    { name: "Pedro Uchoa", imageSrc: "/pedro.jpeg", designation: "Desenvolvimento", color: "#34d399", instagram: "https://www.instagram.com/pedrou1512/", linkedin: "https://www.linkedin.com/in/pedro-uchoaa/" },
    { name: "Leonardo Ramos", imageSrc: "/leo.jpeg", designation: "Desenvolvimento", color: "#fbbf24", instagram: "https://www.instagram.com/leormsv/", linkedin: "https://www.linkedin.com/in/leonardoramosvieira/" },
    { name: "Jaime Almeida", imageSrc: "/jaime.jpeg", designation: "Desenvolvimento", color: "#f472b6", instagram: "https://www.instagram.com/jaime.almeidaa/", linkedin: "https://www.linkedin.com/in/jaimeandradedealmeida/" },
];

export const teamInitials = initials;
